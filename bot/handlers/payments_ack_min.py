# bot/handlers/payments_ack_min.py
"""
Мини‑патч: мгновенно показать пользователю ACK после скрина оплаты,
а всю тяжёлую работу (Notion/уведомление админа) сделать в фоне.

Использование (в вашем фото‑хендлере):
    from bot.handlers.payments_ack_min import handle_payment_proof_ack
    await handle_payment_proof_ack(update, context, payment_type="webinar_joi", product_code="joi")
    return  # остальное сделается в фоне
"""
import asyncio
import logging
from typing import Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.database.notion_payments import create_payment_record  # создаём запись в Payments

log = logging.getLogger(__name__)

def _main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]])

async def handle_payment_proof_ack(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    payment_type: str,
    product_code: Optional[str] = None,
) -> None:
    """
    1) МГНОВЕННО отправляет пользователю ACK с кнопкой «🏠 Главное меню».
    2) В ФОНЕ создаёт запись в Notion (Payments) и (если есть) зовёт ваш notify_admin_payment_submitted().
    """
    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    # --- 1) Мгновенный ACK пользователю ---
    try:
        await chat.send_message(
            "✅ Скриншот оплаты получен. Мы проверим его и свяжемся с вами.",
            reply_markup=_main_menu_kb(),
            disable_web_page_preview=True,
        )
    except Exception as e:
        log.warning("ACK send failed: %s", e)

    # --- 2) Собираем file_id (фото/документ-картинка) ---
    proof_file_id = None
    try:
        if message.photo:
            proof_file_id = message.photo[-1].file_id  # лучшее качество
        elif message.document and message.document.mime_type and message.document.mime_type.startswith("image/"):
            proof_file_id = message.document.file_id
    except Exception:
        pass

    # --- 3) Фоновая задача: Notion + уведомление админа (если есть функция проекта) ---
    async def _bg():
        notion_payment_id = None
        try:
            notion_payment_id = await create_payment_record(
                user_telegram_id=user.id,
                payment_type=payment_type,
                proof_file_id=proof_file_id or "n/a",
                product_code=product_code,     # если передан slug — сразу свяжем с продуктом
                username=user.username,
                name=user.full_name,
            )
            log.info("Payment record created: %s", notion_payment_id)
        except Exception as e:
            log.error("create_payment_record failed: %s", e)

        # Попробуем вызвать ваш проектный уведомитель, если он существует
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
        except Exception as e:
            log.warning("Admin notify skipped/failed: %s", e)

    asyncio.create_task(_bg())
