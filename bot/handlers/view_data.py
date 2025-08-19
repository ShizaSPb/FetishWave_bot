import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.database.notion_db import get_user_data
from bot.services.actions import log_action

logger = logging.getLogger(__name__)


async def view_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("view_data_request", user_id)

    try:
        user_data = await get_user_data(user_id)

        if user_data:
            log_action("view_data_success", user_id)
            response = (
                f"📋 Ваши данные:\n"
                f"Имя: {user_data['name']}\n"
                f"Email: {user_data['email']}\n"
                f"Логин: {user_data['username']}\n"
                f"Язык: {user_data['language']}\n"
                f"Дата регистрации: {user_data['reg_date']}"
            )
        else:
            log_action("view_data_not_found", user_id)
            response = "❌ Данные не найдены. Пройдите регистрацию /register"

        await update.message.reply_text(response)

    except Exception as e:
        log_action("view_data_error", user_id, {"error": str(e)})
        logger.error(f"Error in view_data: {e}", exc_info=True)
        await update.message.reply_text("⚠️ Произошла ошибка при получении данных")


view_data_handler = CommandHandler('viewdata', view_data)