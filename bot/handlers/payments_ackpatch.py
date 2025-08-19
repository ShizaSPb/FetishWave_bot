from __future__ import annotations

import asyncio
import logging
import time
from typing import Iterable, Optional

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

# Единственное место для логирования действий
from bot.services.actions import log_action

# Поддержим обе переменные из config: ADMIN_IDS (предпочтительно) и ADMIN_CHAT_IDS (устар.)
try:
    from config import ADMIN_IDS  # type: ignore
except Exception:
    ADMIN_IDS = []  # type: ignore[assignment]
try:
    from config import ADMIN_CHAT_IDS  # type: ignore
except Exception:
    ADMIN_CHAT_IDS = []  # type: ignore[assignment]

log = logging.getLogger(__name__)

MAIN_MENU_CALLBACK = "go_main_menu"  # если у вас иначе — поменяйте тут


def _admin_ids() -> Iterable[int]:
    raw = []
    if isinstance(ADMIN_IDS, (list, tuple)):
        raw.extend(list(ADMIN_IDS))
    if isinstance(ADMIN_CHAT_IDS, (list, tuple)):
        raw.extend(list(ADMIN_CHAT_IDS))
    elif isinstance(ADMIN_CHAT_IDS, str):
        raw.extend([x.strip() for x in ADMIN_CHAT_IDS.split(",") if x.strip()])
    out: list[int] = []
    for x in raw:
        try:
            out.append(int(x))
        except Exception:
            pass
    # убираем дубли
    return list(dict.fromkeys(out))


def _user_ack_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)]]
    )


def _admin_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"admin_pay_ok:{payment_id}"),
            InlineKeyboardButton("❌ Отклонить",   callback_data=f"admin_pay_reject:{payment_id}"),
        ]
    ])


async def _fallback_notify_admins(
    context: ContextTypes.DEFAULT_TYPE,
    *, payment_id: int,
    caption: str,
    file_kind: Optional[str],
    file_id: Optional[str],
) -> None:
    """
    Простой фолбэк-нотификатор для админов.
    НИКОГДА не роняет основной поток.
    """
    for admin_id in _admin_ids():
        try:
            if file_kind == "photo" and file_id:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=caption,
                    reply_markup=_admin_keyboard(payment_id),
                    disable_notification=True,
                )
            elif file_kind == "document" and file_id:
                await context.bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=caption,
                    reply_markup=_admin_keyboard(payment_id),
                    disable_notification=True,
                )
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=caption,
                    reply_markup=_admin_keyboard(payment_id),
                    disable_web_page_preview=True,
                    disable_notification=True,
                )
        except Exception:
            log.exception("Не удалось отправить уведомление админу %s по оплате %s", admin_id, payment_id)


async def _bg_process_payment_proof(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *, payment_type: Optional[str],
    product_code: Optional[str],
    file_kind: Optional[str],
    file_id: Optional[str],
    file_unique_id: Optional[str],
    stub_payment_id: int,
) -> None:
    """
    Фоновая обработка: создать запись в БД/Notion (если нужно) и уведомить админов.
    Любые исключения ловим и логируем.
    """
    user = update.effective_user
    caption = (
        f"🧾 Новая оплата от @{user.username or user.id}\n"
        f"User ID: {user.id}\n"
        f"Payment ID: {stub_payment_id}\n"
        f"Тип: {payment_type or '-'} | Код: {product_code or '-'}\n"
        f"Статус: pending"
    )

    # Если в проекте есть специализированный уведомитель админов — используем его
    used_project_notifier = False
    try:
        from bot.handlers.admin_payments import notify_admin_payment_submitted  # type: ignore
        try:
            await notify_admin_payment_submitted(  # type: ignore[misc]
                context=context,
                user_id=user.id,
                payment_id=stub_payment_id,
                caption=caption,
                file_kind=file_kind,
                file_id=file_id,
                payment_type=payment_type,
                product_code=product_code,
            )
            used_project_notifier = True
        except Exception:
            log.exception("notify_admin_payment_submitted упал")
    except Exception:
        # нет проектной функции — это нормально
        pass

    if not used_project_notifier:
        try:
            await _fallback_notify_admins(
                context,
                payment_id=stub_payment_id,
                caption=caption,
                file_kind=file_kind,
                file_id=file_id,
            )
        except Exception:
            log.exception("fallback-нотификатор админов упал")

    # Финальный лог действия
    try:
        log_action(
            "payment_proof_processed_bg",
            user_id=user.id,
            payment_id=stub_payment_id,
            file_kind=file_kind,
            has_file=bool(file_id),
            file_unique_id=file_unique_id,
            payment_type=payment_type,
            product_code=product_code,
        )
    except Exception:
        pass


async def handle_payment_proof_with_ack(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *, payment_type: Optional[str] = None,
    product_code: Optional[str] = None,
) -> None:
    """
    Главный вход: вызывать из вашего текущего обработчика.
    1) СРАЗУ отправляет ACK пользователю (await).
    2) Фоновой задачей (create_task) обрабатывает админов/БД.
    """
    msg = update.effective_message
    user = update.effective_user

    # --- Извлекаем файл (photo/document) ---
    file_kind: Optional[str] = None
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None
    if msg and msg.photo:
        file_kind = "photo"
        file_id = msg.photo[-1].file_id
        file_unique_id = msg.photo[-1].file_unique_id
    elif msg and msg.document and (msg.document.mime_type or "").startswith("image/"):
        file_kind = "document"
        file_id = msg.document.file_id
        file_unique_id = msg.document.file_unique_id

    # --- 1) СНАЧАЛА отвечаем пользователю ---
    try:
        await msg.reply_text(
            "✅ Скриншот оплаты получен. Мы проверим его и свяжемся с вами.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Главное меню", callback_data=MAIN_MENU_CALLBACK)
            ]]),
            disable_web_page_preview=True,
        )
    except Exception:
        log.exception("Не удалось отправить ACK пользователю %s", getattr(user, "id", None))

    # Дедупликация по file_unique_id (микро-защита от дабл-тапа)
    if file_unique_id:
        dedupe = context.user_data.setdefault("_proof_seen", set())
        if isinstance(dedupe, set) and file_unique_id in dedupe:
            # Уже обрабатывали этот файл — просто выходим
            return
        try:
            dedupe.add(file_unique_id)
        except Exception:
            pass

    # --- Лог снимаем отдельно ---
    try:
        log_action(
            "payment_proof_ack_sent",
            user_id=getattr(user, "id", None),
            username=getattr(user, "username", None),
            file_kind=file_kind,
            has_file=bool(file_id),
            file_unique_id=file_unique_id,
            payment_type=payment_type,
            product_code=product_code,
        )
    except Exception:
        pass

    # --- 2) ФОНОВАЯ обработка ---
    # Простая генерация платежного ID (если у проекта нет своего репозитория на этом этапе)
    stub_payment_id = int(time.time())
    context.application.create_task(
        _bg_process_payment_proof(
            update, context,
            payment_type=payment_type,
            product_code=product_code,
            file_kind=file_kind,
            file_id=file_id,
            file_unique_id=file_unique_id,
            stub_payment_id=stub_payment_id,
        )
    )


# На вкус: можно сразу экспортировать готовый handler, если удобно регистрировать напрямую
handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_payment_proof_with_ack)
