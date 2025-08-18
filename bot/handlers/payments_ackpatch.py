# bot/handlers/payments_ackpatch.py
"""
Асинхронный ACK после скриншота оплаты + простой фолбэк-нотификатор для админов.

- Пользователь сразу получает сообщение "✅ Скриншот оплаты получен..." + кнопку "🏠 Главное меню".
- В фоне создаётся страница в Notion (Payments) и отправляется уведомление для админов.
- Если проектный уведомитель отсутствует/упал, сработает простой бродкаст по ADMIN_CHAT_IDS.
"""

import asyncio
import logging
from typing import Optional, Iterable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.database.notion_payments import create_payment_record  # создаём запись в Payments

try:
    # В config может лежать список, кортеж или строка через запятую
    from config import ADMIN_CHAT_IDS  # type: ignore
except Exception:
    ADMIN_CHAT_IDS = []  # нет конфига — пусто

log = logging.getLogger(__name__)


def _main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])


def _normalize_admin_ids(value) -> list[int]:
    ids: list[int] = []
    try:
        if not value:
            return ids
        if isinstance(value, (list, tuple, set)):
            for v in value:
                try:
                    ids.append(int(v))
                except Exception:
                    pass
            return ids
        if isinstance(value, str):
            parts = value.replace(";", ",").replace(" ", ",").split(",")
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                try:
                    ids.append(int(p))
                except Exception:
                    pass
            return ids
    except Exception:
        pass
    return ids


async def _notify_admins_simple(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    admin_ids,
    user,
    payment_type: str,
    notion_payment_id: Optional[str],
    proof_file_id: Optional[str],
    proof_kind: str,  # "photo" | "document" | "none"
    product_code: Optional[str],
):
    if not admin_ids:
        return

    caption = (
        f"📩 Новый платёж (fallback)\n\n"
        f"Пользователь: @{user.username or '—'} (id {user.id})\n"
        f"Тип/код: {payment_type} | slug: {product_code or '—'}\n"
        f"Notion Payment: {notion_payment_id or '—'}"
    )

    tasks = []
    for admin_id in admin_ids:
        try:
            if proof_file_id and proof_kind == "photo":
                tasks.append(context.bot.send_photo(chat_id=admin_id, photo=proof_file_id, caption=caption))
            elif proof_file_id and proof_kind == "document":
                tasks.append(context.bot.send_document(chat_id=admin_id, document=proof_file_id, caption=caption))
            else:
                tasks.append(context.bot.send_message(chat_id=admin_id, text=caption))
        except Exception as e:
            log.warning("Failed to enqueue admin notify to %s: %s", admin_id, e)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def handle_payment_proof_with_ack(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    payment_type: str,
    product_code: Optional[str] = None,
) -> None:
    """
    1) Сразу отправляет пользователю ACK: «✅ Скриншот оплаты получен…» + кнопка в Главное меню.
    2) В фоне создаёт страницу в Notion (Payments) и уведомляет админов.
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    # --- 1) Мгновенный ACK пользователю ---
    try:
        # защита от дублей: не чаще 10 сек
        last = context.user_data.get("_last_payment_ack_ts")
        now = asyncio.get_event_loop().time()
        if not last or (now - float(last) > 10.0):
            await chat.send_message(
                "✅ Скриншот оплаты получен. Мы проверим его и свяжемся с вами.",
                reply_markup=_main_menu_kb(),
                disable_web_page_preview=True,
            )
            context.user_data["_last_payment_ack_ts"] = now
    except Exception as e:
        log.warning("Failed to send ACK to user: %s", e)

    # Вытащим file_id
    proof_file_id = None
    proof_kind = "none"
    try:
        if message.photo:
            proof_file_id = message.photo[-1].file_id
            proof_kind = "photo"
        elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
            proof_file_id = message.document.file_id
            proof_kind = "document"
    except Exception:
        pass

    # --- 2) Фоновые задачи (Notion + админы) ---
    async def _bg():
        notion_payment_id = None
        try:
            notion_payment_id = await create_payment_record(
                user_telegram_id=user.id,
                payment_type=payment_type,
                proof_file_id=proof_file_id or "n/a",
                product_code=product_code,
                username=user.username,
                name=user.full_name,
            )
            log.info("Payment record created: %s", notion_payment_id)
        except Exception as e:
            log.error("create_payment_record failed: %s", e)

        # 1) проектный уведомитель
        notified = False
        try:
            from bot.handlers.admin_payments import notify_admin_payment_submitted  # type: ignore
            if notion_payment_id:
                await notify_admin_payment_submitted(
                    context=context,
                    user=user,
                    payment_type=payment_type,
                    proof_file_id=proof_file_id,
                    notion_payment_id=notion_payment_id,
                    product_code=product_code,
                )
                notified = True
        except Exception as e:
            log.warning("Admin notify via project handler failed: %s", e)

        # 2) фолбэк по ADMIN_CHAT_IDS
        if not notified:
            admin_ids = _normalize_admin_ids(ADMIN_CHAT_IDS)
            try:
                await _notify_admins_simple(
                    context,
                    admin_ids=admin_ids,
                    user=user,
                    payment_type=payment_type,
                    notion_payment_id=notion_payment_id,
                    proof_file_id=proof_file_id,
                    proof_kind=proof_kind,
                    product_code=product_code,
                )
            except Exception as e:
                log.warning("Fallback admin broadcast failed: %s", e)

    asyncio.create_task(_bg())
