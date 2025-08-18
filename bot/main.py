import logging
from telegram import Update
from telegram.ext import Application
from config import BOT_TOKEN
from bot.handlers import handlers
from bot.utils.logger import setup_logging

# Инициализация логирования
setup_logging()
logger = logging.getLogger(__name__)

def run_bot():
    try:
        logger.info("Starting bot...")
        app = Application.builder().token(BOT_TOKEN).build()

        for handler in handlers:
            app.add_handler(handler)

        logger.info("Bot started successfully")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.critical(f"Bot failed to start: {str(e)}", exc_info=True)
        raise




if __name__ == "__main__":
    run_bot()