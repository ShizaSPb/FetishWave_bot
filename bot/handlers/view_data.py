import logger

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.database.notion_db import get_user_data


async def view_data(update: Update, _: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        user_data = await get_user_data(user_id)

        if user_data:
            response = (
                f"📋 Ваши данные:\n"
                f"Имя: {user_data['name']}\n"
                f"Email: {user_data['email']}\n"
                f"Логин: {user_data['username']}\n"
                f"Язык: {user_data['language']}\n"
                f"Дата регистрации: {user_data['reg_date']}"
            )
        else:
            response = "❌ Данные не найдены. Пройдите регистрацию /register"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error in view_data: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при получении данных")


view_data_handler = CommandHandler('viewdata', view_data)