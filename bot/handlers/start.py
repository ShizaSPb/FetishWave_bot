from telegram import Update
from telegram.ext import CommandHandler

async def start_command(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для продаж.\n"
        "Используй /register чтобы зарегистрироваться."
    )

# Создаем обработчик команды
handler = CommandHandler("start", start_command)