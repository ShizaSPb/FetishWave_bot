from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.database.notion_db import get_user_data


async def view_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = await get_user_data(user_id)

    if user_data:
        response = (
            f"📋 Ваши данные:\n"
            f"Имя: {user_data['name']}\n"
            f"Email: {user_data['email']}\n"
            f"Дата регистрации: {user_data['reg_date']}"
        )
    else:
        response = "❌ Данные не найдены. Пройдите регистрацию /register"

    await update.message.reply_text(response)


handler = CommandHandler('viewdata', view_data)