# bot/handlers/proofs_guard.py
"""
Safety net: гарантирует мгновенный ACK при получении скриншота оплаты,
даже если основной поток/хендлер завис или упал.

Как работает:
- В месте, где ты просишь «Пришлите скриншот оплаты», вызови mark_expect_proof(...).
- Глобальный MessageHandler (group=-1) ловит фото/изображение-документ в ЛС,
  проверяет флаг и, если он установлен и не истёк, отправляет ACK и уводит остальное в фон.
"""

import time
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.handlers.payments_ackpatch import handle_payment_proof_with_ack
from bot.utils.product_codes import type_to_slug

log = logging.getLogger(__name__)

FLAG_KEY = "_expect_payment_proof"  # в context.user_data
TTL_SECONDS = 600  # 10 минут на загрузку скрина

def mark_expect_proof(context: ContextTypes.DEFAULT_TYPE, *, payment_type: str, product_code: Optional[str] = None, ttl: int = TTL_SECONDS) -> None:
    """Вызывай это сразу после показа экрана с просьбой прислать скриншот."""
    context.user_data[FLAG_KEY] = {
        "payment_type": str(payment_type),
        "product_code": (product_code or type_to_slug(str(payment_type))),
        "set_at": time.time(),
        "ttl": int(ttl),
    }

def _is_flag_active(context: ContextTypes.DEFAULT_TYPE) -> bool:
    data = context.user_data.get(FLAG_KEY)
    if not isinstance(data, dict):
        return False
    set_at = float(data.get("set_at", 0))
    ttl = int(data.get("ttl", TTL_SECONDS))
    return (time.time() - set_at) <= ttl

async def _guard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальный перехватчик фото/картинок в ЛС. Ничего не делает, если флаг не активен."""
    if not _is_flag_active(context):
        return

    data = context.user_data.get(FLAG_KEY) or {}
    payment_type = data.get("payment_type") or "unknown"
    product_code = data.get("product_code")

    try:
        await handle_payment_proof_with_ack(
            update,
            context,
            payment_type=payment_type,
            product_code=product_code,
        )
        # Сбросим флаг, чтобы не ACK-ать каждую картинку подряд
        context.user_data.pop(FLAG_KEY, None)
    except Exception as e:
        log.error("proofs_guard: failed to handle proof: %s", e)

def register_proofs_guard(application) -> None:
    """
    Подключи это в bot/main.py сразу после создания application (group=-1),
    чтобы ACK всегда успевал уйти пользователю.
    """
    f = (filters.ChatType.PRIVATE & (filters.PHOTO | filters.Document.IMAGE))
    application.add_handler(MessageHandler(f, _guard_handler), group=-1)
