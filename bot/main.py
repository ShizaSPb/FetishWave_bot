import logging
from telegram import Update
from telegram.ext import Application
from config import BOT_TOKEN
from bot.handlers import handlers

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    for handler in handlers:
        app.add_handler(handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    run_bot()