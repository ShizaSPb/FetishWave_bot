from __future__ import annotations

import logging
from typing import List, Optional

from telegram import Update
from telegram.error import Forbidden, TimedOut, RetryAfter, NetworkError, BadRequest
from telegram.ext import ContextTypes

from bot.services.actions import log_action

# Админы (best-effort)
try:
    from config import ADMIN_IDS  # type: ignore
except Exception:
    ADMIN_IDS: List[int] = []

log = logging.getLogger("errors")


def _can_message_user(update: Optional[Update]) -> bool:
    return bool(update and update.effective_chat)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error

    # Логи
    log.exception("Unhandled error in handler")
    try:
        log_action(
            "handler_error",
            error_type=type(err).__name__ if err else "Unknown",
            error=str(err),
            update_type=type(update).__name__ if update else None,
            user_id=getattr(getattr(update, "effective_user", None), "id", None),
            chat_id=getattr(getattr(update, "effective_chat", None), "id", None),
        )
    except Exception:
        pass

    # Тихо игнорируем типовые ошибки
    if isinstance(err, (Forbidden, RetryAfter, TimedOut, NetworkError)):
        return
    if isinstance(err, BadRequest) and "message is not modified" in str(err).lower():
        return

    # Ответ пользователю (если есть куда)
    try:
        if _can_message_user(update):  # type: ignore[arg-type]
            await context.bot.send_message(  # type: ignore[attr-defined]
                chat_id=update.effective_chat.id,  # type: ignore[attr-defined]
                text="😕 Возникла ошибка. Попробуйте ещё раз или зайдите в меню: /start",
                disable_web_page_preview=True,
            )
    except Exception:
        pass

    # Короткое уведомление первому админу
    try:
        admin_id = next((a for a in ADMIN_IDS if isinstance(a, int)), None)
        if admin_id:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"⚠️ Ошибка: {type(err).__name__}: {str(err)[:800]}",
                disable_web_page_preview=True,
            )
    except Exception:
        pass
