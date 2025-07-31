from telegram.ext import Application
from config import BOT_TOKEN
from bot.handlers import handlers

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()

    for handler in handlers:
        app.add_handler(handler)

    app.run_polling()

if __name__ == "__main__":
    run_bot()