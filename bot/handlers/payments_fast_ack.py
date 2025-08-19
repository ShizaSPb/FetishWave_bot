
# bot/handlers/payments_fast_ack.py
"""
Быстрый ACK + жёсткая очистка приглашения.
Обновления v7:
- Сразу после получения файла удаляем сообщение‑приглашение «📤 Загрузите скриншот…»
  не только по `upload_prompt_msg_id`, но и по `last_menu_message_id` (на случай,
  если приглашение сохранялось как «последнее меню»).
- Очищаем соответствующие ключи из user_data, чтобы другая логика не пыталась редактировать удалённое сообщение.
"""
from __future__ import annotations

import logging
import time
from typing import Optional, Iterable

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ApplicationHandlerStop,
)

# --- Вспомогательные импорты проекта (с безопасными фоллбэками) ---
try:
    from config import ADMIN_IDS  # set[int] или list[int]
except Exception:
    ADMIN_IDS = []  # type: ignore

try:
    from bot.utils.keyboards import get_main_menu_keyboard
except Exception:
    def get_main_menu_keyboard(lang: str):
        return None

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
        return None

try:
    from bot.services.actions import log_action
except Exception:
    def log_action(*args, **kwargs):
        pass

log = logging.getLogger(__name__)

# ---- Локализация кнопки ----
def _btn_text(lang: str) -> str:
    if str(lang).startswith('sr'):
        return "Назад у главни мени"
    elif str(lang).startswith('en'):
        return "Back to main menu"
    return "Вернуться в главное меню"

def _ack_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(_btn_text(lang), callback_data="return_to_main")
    ]])

# ---- Служебные функции ----
def _iter_admins() -> Iterable[int]:
    ids = []
    try:
        ids = list(ADMIN_IDS)  # type: ignore
    except Exception:
        pass
    return [i for i in ids if isinstance(i, int) and i > 0]

async def _bg_notify_admins(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    payment_id: int,
    payment_type: Optional[str],
    product_code: Optional[str],
    file_kind: Optional[str],
    file_id: Optional[str],
) -> None:
    user = update.effective_user
    caption = (
        f"🧾 Новая оплата от @{getattr(user, 'username', None) or user.id}\n"
        f"User ID: {user.id}\n"
        f"Payment ID: {payment_id}\n"
        f"Тип: {payment_type or '-'} | Код: {product_code or '-'}"
    )

    for admin_id in _iter_admins():
        try:
            if file_kind == 'photo' and update.effective_message and update.effective_message.photo:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=caption,
                    reply_markup=get_admin_payment_actions_kb(str(payment_id)),
                )
            elif file_kind in ('image','pdf') and update.effective_message and update.effective_message.document:
                await context.bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=caption,
                    reply_markup=get_admin_payment_actions_kb(str(payment_id)),
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=caption,
                    reply_markup=get_admin_payment_actions_kb(str(payment_id)),
                )
        except Exception:
            log.exception("Не удалось уведомить админа %s", admin_id)

    try:
        log_action(
            "admin_payment_notified",
            user_id=user.id,
            payment_id=payment_id,
            payment_type=payment_type,
            product_code=product_code,
            has_file=bool(file_id),
            file_kind=file_kind,
        )
    except Exception:
        pass

# ---- Быстрый ACK ----
async def handle_fast_payment_ack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if not msg:
        return

    if not context.user_data.get('awaiting_screenshot'):
        return

    lang = context.user_data.get('lang', 'ru')
    payment_type = context.user_data.get('current_payment_type')
    product_code = context.user_data.get('product_code')

    # Извлечение файла
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
            return  # другой тип — пропускаем, пусть обработают другие хендлеры
    else:
        return

    # Сохраняем id сообщения со скрином/документом
    context.user_data['last_payment_proof_msg_id'] = msg.message_id

    # Дедупликация
    seen = context.user_data.setdefault('_proof_seen', set())
    if isinstance(seen, set) and file_unique_id and file_unique_id in seen:
        raise ApplicationHandlerStop()
    if isinstance(seen, set) and file_unique_id:
        seen.add(file_unique_id)

    # --- СРАЗУ удаляем приглашение «📤 Загрузите скриншот…» ---
    ids_to_try = []
    # 1) явный id приглашения, если его сохраняли
    up_id = context.user_data.pop('upload_prompt_msg_id', None)
    if up_id:
        ids_to_try.append(up_id)
    # 2) на многих экранах приглашение сохраняют как "последнее меню"
    lm_id = context.user_data.pop('last_menu_message_id', None)
    if lm_id:
        ids_to_try.append(lm_id)
    # подчищаем ещё тип меню, чтобы другие обработчики не опирались на удалённое сообщение
    context.user_data.pop('last_menu_type', None)

    if ids_to_try and update.effective_chat:
        for mid in ids_to_try:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=mid)
            except Exception:
                pass

    # 1) Сразу отвечаем пользователю + инлайн-кнопка
    ack_msg = None
    try:
        ack_msg = await msg.reply_text(
            "✅ Скриншот оплаты получен. Мы проверим его и свяжемся с вами.",
            reply_markup=_ack_keyboard(lang),
            disable_web_page_preview=True,
        )
    except Exception:
        log.exception("Не удалось отправить ACK пользователю")

    # Сохраняем id ACK, чтобы можно было убрать при возврате в меню
    if ack_msg:
        context.user_data['last_payment_ack_msg_id'] = ack_msg.message_id

    # Сбрасываем ожидание
    context.user_data.pop('awaiting_screenshot', None)

    # 2) Фон: уведомление админам
    stub_payment_id = int(time.time())
    context.application.create_task(
        _bg_notify_admins(
            update, context,
            payment_id=stub_payment_id,
            payment_type=payment_type,
            product_code=product_code,
            file_kind=file_kind,
            file_id=file_id,
        )
    )

    # 3) Остановить остальные обработчики
    raise ApplicationHandlerStop()

# ---- Callback: возврат в главное меню ----
async def on_return_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat = update.effective_chat
    try:
        await query.answer()
    except Exception:
        pass

    # Удаляем ACK (наше сообщение)
    ack_id = context.user_data.pop('last_payment_ack_msg_id', None)
    if ack_id and chat:
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=ack_id)
        except Exception:
            pass

    # Пытаемся удалить сообщение со скриншотом/документом (может не получиться в личке)
    proof_id = context.user_data.pop('last_payment_proof_msg_id', None)
    if proof_id and chat:
        try:
            await context.bot.delete_message(chat_id=chat.id, message_id=proof_id)
        except Exception:
            pass

    # Переход в главное меню
    try:
        await show_main_menu(update, context, cleanup_previous=True)
    except Exception:
        if chat:
            await context.bot.send_message(
                chat_id=chat.id,
                text="Главное меню",
                reply_markup=get_main_menu_keyboard(context.user_data.get('lang', 'ru'))
            )

# Экспорт набора хендлеров
ack_message_handler = MessageHandler(
    (filters.ChatType.PRIVATE & (filters.PHOTO | filters.Document.ALL)),
    handle_fast_payment_ack
)
back_button_handler = CallbackQueryHandler(on_return_to_main, pattern="^return_to_main$")

handlers = [ack_message_handler, back_button_handler]
