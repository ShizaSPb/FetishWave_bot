import re
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from bot.database.notion_db import add_user_to_notion
from bot.handlers.shared import get_user_language
from bot.utils.languages import LANGUAGES

# Шаги диалога
NAME, EMAIL = range(2)

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = get_user_language(context)
    await update.message.reply_text(LANGUAGES[lang]["enter_email"])
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    lang = get_user_language(context)

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        await update.message.reply_text("❌ " + LANGUAGES[lang]["enter_email"])
        return EMAIL

    user = update.effective_user
    user_data = {
        "name": context.user_data['name'],
        "telegram_id": user.id,
        "username": user.username,
        "email": email,
        "language": lang,
        "reg_date": datetime.now().isoformat()
    }

    if await add_user_to_notion(user_data):
        await update.message.reply_text("✅ Данные сохранены!")
    else:
        await update.message.reply_text("❌ Ошибка сохранения")

    return ConversationHandler.END

register_conversation_handler = ConversationHandler(
    entry_points=[],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)]
    },
    fallbacks=[]
)