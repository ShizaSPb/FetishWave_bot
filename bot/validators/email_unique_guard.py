# bot/validators/email_unique_guard.py
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.notion_users_unique import email_is_free, normalize_email, get_existing_user_telegram_id

MESSAGE_ALREADY_USED = ("Эта почта уже используется другим аккаунтом.\n"
                        "Введите другой email или зайдите в Личный кабинет, если это ваша почта.")

async def ensure_email_unique_or_fail(update: Update, context: ContextTypes.DEFAULT_TYPE, email: str) -> str | None:
    """Проверка уникальности. Возвращает нормализованный email ИЛИ None (если занят — отправляет сообщение и останавливает шаг)."""
    e = normalize_email(email)
    ok = await email_is_free(e, update.effective_user.id)
    if ok:
        return e
    # почта занята другим TG-пользователем
    await update.effective_message.reply_text(MESSAGE_ALREADY_USED)
    return None
