
# bot/handlers/payments_fast_ack.py
"""
v13: быстрые ХЕНДЛЕРЫ БЛОКИРУЮТ цепочку (block=True) + мгновенный UX
- Возврат к семантике ApplicationHandlerStop: после нашего хендлера другие обработчики не запускаются.
- Уникальный callback_data для кнопки: "back_main_fast_v1".
- Все тяжёлые вещи (Notion/рассылка админам/удаление сообщений) уходят в фон, UI не ждёт.
- Сразу удаляем приглашение «📤 Загрузите скриншот…» по upload_prompt_msg_id и/или last_menu_message_id.
- Поддержка: photo, document image/*, application/pdf.
"""
from __future__ import annotations

import logging
import time
import asyncio
import inspect
from typing import Optional, Iterable, Any, Callable

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ApplicationHandlerStop,
)

# --- Конфиг/утилиты ---
try:
    from config import ADMIN_IDS
except Exception:
    ADMIN_IDS = []  # type: ignore

try:
    from bot.utils.keyboards import get_main_menu_keyboard
except Exception:
    def get_main_menu_keyboard(lang: str):
        return None

# show_main_menu может быть тяжёлым — в кнопке мы отправляем лёгкое меню напрямую
try:
    from .menu import show_main_menu
except Exception:
    async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, cleanup_previous: bool = True):
        if update.effective_chat:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Главное меню",
                reply_markup=get_main_menu_keyboard(context.user_data.get('lang', 'ru')),
            )

try:
    from bot.utils.admin_keyboards import get_admin_payment_actions_kb
except Exception:
    def get_admin_payment_actions_kb(payment_id: str):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"adm_pay:confirm:{payment_id}"),
        ]])

# Оперативная память (best‑effort)
try:
    from .admin_payments import remember_pending_payment  # type: ignore
except Exception:
    def remember_pending_payment(*args, **kwargs):
        pass

# Интеграция с Notion
try:
    from bot.database.notion_payments import create_payment_record  # type: ignore
except Exception:
    create_payment_record = None  # type: ignore

log = logging.getLogger(__name__)

BACK_CB = "back_main_fast_v1"

# ---- Локализация кнопки ----
def _btn_text(lang: str) -> str:
    if str(lang).startswith('sr'):
        return "Назад у главни мени"
    elif str(lang).startswith('en'):
        return "Back to main menu"
    return "Вернуться в главное меню"

def _ack_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_btn_text(lang), callback_data=BACK_CB)
    ]])

# ---- Вспомогательные ----
def _iter_admins() -> Iterable[int]:
    ids = []
    try:
        ids = list(ADMIN_IDS)  # type: ignore
    except Exception:
        pass
    return [i for i in ids if isinstance(i, int) and i > 0]

async def _maybe_async(func: Callable[..., Any], /, *args, **kwargs):
    "Вызывает func: если это корутина — await; если синхронная — to_thread."
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return await asyncio.to_thread(func, *args, **kwargs)

async def _bg_persist_and_notify(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    user_id: int,
    username: Optional[str],
    payment_type: Optional[str],
    product_code: Optional[str],
    file_kind: str,
    file_id: str,
) -> None:
    # 1) Создаём запись в Notion (не блокируем event loop)
    notion_payment_id: Optional[str] = None
    if create_payment_record is not None:
        for kwargs in (
            dict(user_telegram_id=user_id, payment_type=payment_type, product_code=product_code, proof_file_id=file_id, username=username, name=None),
            dict(user_telegram_id=user_id, payment_type=payment_type, proof_file_id=file_id),
            dict(user_telegram_id=user_id, payment_type=payment_type),
        ):
            try:
                pid = await _maybe_async(create_payment_record, **kwargs)
                if pid:
                    notion_payment_id = str(pid)
                    break
            except Exception:
                log.exception("create_payment_record failed with kwargs=%s", list(kwargs.keys()))

    # 2) Сохраняем в память (best‑effort)
    try:
        remember_pending_payment(
            context=context,
            user_id=user_id,
            payment_type=payment_type,
            product_code=product_code,
            notion_payment_id=notion_payment_id,
        )
    except Exception:
        pass

    # 3) Рассылаем админам
    payload = f"{notion_payment_id}|{user_id}" if notion_payment_id else str(int(time.time()))
    caption_id = notion_payment_id or '—'
    kb = get_admin_payment_actions_kb(payload)

    caption = (
        f"🧾 Новая оплата от @{username or user_id}\n"
        f"User ID: {user_id}\n"
        f"Payment ID: {caption_id}\n"
        f"Тип: {payment_type or '-'} | Код: {product_code or '-'}\n"
        f"Статус: pending"
    )

    for admin_id in _iter_admins():
        try:
            if file_kind == 'photo':
                await context.bot.send_photo(chat_id=admin_id, photo=file_id, caption=caption, reply_markup=kb)
            else:
                await context.bot.send_document(chat_id=admin_id, document=file_id, caption=caption, reply_markup=kb)
        except Exception:
            log.exception("Не удалось уведомить админа %s", admin_id)

# ---- Главный обработчик ----
async def handle_fast_payment_ack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return
    if not context.user_data.get('awaiting_screenshot'):
        return

    user = update.effective_user
    lang = context.user_data.get('lang', 'ru')
    payment_type = context.user_data.get('current_payment_type')
    product_code = context.user_data.get('product_code')

    file_kind: Optional[str] = None
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None

    if msg.photo:
        file_kind = 'photo'
        file_id = msg.photo[-1].file_id
        file_unique_id = msg.photo[-1].file_unique_id
    elif msg.document:
        mime = (msg.document.mime_type or '').lower()
        if mime.startswith('image/'):
            file_kind = 'image'
            file_id = msg.document.file_id
            file_unique_id = msg.document.file_unique_id
        elif mime == 'application/pdf':
            file_kind = 'pdf'
            file_id = msg.document.file_id
            file_unique_id = msg.document.file_unique_id
        else:
            return
    else:
        return

    context.user_data['last_payment_proof_msg_id'] = msg.message_id

    seen = context.user_data.setdefault('_proof_seen', set())
    if isinstance(seen, set) and file_unique_id and file_unique_id in seen:
        raise ApplicationHandlerStop()
    if isinstance(seen, set) and file_unique_id:
        seen.add(file_unique_id)

    # СРАЗУ удаляем приглашение «📤 Загрузите скриншот…»
    ids_to_try = []
    up_id = context.user_data.pop('upload_prompt_msg_id', None)
    if up_id:
        ids_to_try.append(up_id)
    lm_id = context.user_data.pop('last_menu_message_id', None)
    if lm_id:
        ids_to_try.append(lm_id)
    context.user_data.pop('last_menu_type', None)
    if ids_to_try and update.effective_chat:
        for mid in ids_to_try:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
            except Exception:
                pass

    # ACK + кнопка (мгновенно)
    ack_msg = None
    try:
        ack_msg = await msg.reply_text(
            "✅ Скриншот оплаты получен. Мы проверим его и свяжемся с вами.",
            reply_markup=_ack_keyboard(lang),
            disable_web_page_preview=True,
        )
    except Exception:
        log.exception("Не удалось отправить ACK пользователю")
    if ack_msg:
        context.user_data['last_payment_ack_msg_id'] = ack_msg.message_id

    # Сбрасываем ожидание
    context.user_data.pop('awaiting_screenshot', None)

    # Фоновая задача: Notion + уведомления админам (не блокируем цикл)
    try:
        context.application.create_task(
            _bg_persist_and_notify(
                context,
                user_id=user.id,
                username=getattr(user, 'username', None),
                payment_type=payment_type,
                product_code=product_code,
                file_kind='photo' if file_kind == 'photo' else 'document',
                file_id=file_id or '',
            )
        )
    except Exception:
        log.exception("Не удалось запустить фоновую persist+notify")

    # СТОП — больше никакие обработчики на это фото не должны запускаться
    raise ApplicationHandlerStop()

# ---- Callback: возврат в главное меню ----
async def on_return_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat = update.effective_chat

    # мгновенный ответ, чтобы убрать спиннер
    try:
        await query.answer()
    except Exception:
        pass

    # сразу показываем лёгкое меню (без БД)
    try:
        await context.bot.send_message(
            chat_id=chat.id,
            text="Главное меню",
            reply_markup=get_main_menu_keyboard(context.user_data.get('lang', 'ru')),
        )
    except Exception:
        pass

    # уборку делаем в фоне
    ack_id = context.user_data.pop('last_payment_ack_msg_id', None)
    proof_id = context.user_data.pop('last_payment_proof_msg_id', None)

    async def _cleanup():
        if chat and ack_id:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=ack_id)
            except Exception:
                pass
        if chat and proof_id:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=proof_id)
            except Exception:
                pass

    try:
        context.application.create_task(_cleanup())
    except Exception:
        pass

    # СТОП — чтобы другие CallbackQueryHandler не перехватывали этот клик
    raise ApplicationHandlerStop()

# Экспорт хендлеров — БЕЗ block=False (по умолчанию block=True)
ack_message_handler = MessageHandler(
    (filters.ChatType.PRIVATE & (filters.PHOTO | filters.Document.ALL)),
    handle_fast_payment_ack,
)
back_button_handler = CallbackQueryHandler(
    on_return_to_main,
    pattern=r"^" + BACK_CB + r"$",
)

handlers = [ack_message_handler, back_button_handler]
