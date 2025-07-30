import filters
from telegram import Update
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler

# Шаги диалога
NAME, EMAIL = range(2)

async def register_command(update: Update, context):
    await update.message.reply_text("Введите ваше имя:")
    return NAME

async def get_name(update: Update, context):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш email:")
    return EMAIL

async def get_email(update: Update, context):
    context.user_data['email'] = update.message.text
    # Здесь позже добавим сохранение в Notion
    await update.message.reply_text("Регистрация завершена!")
    return ConversationHandler.END

# Создаем обработчик диалога
handler = ConversationHandler(
    entry_points=[CommandHandler("register", register_command)],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        EMAIL: [MessageHandler(filters.TEXT, get_email)],
    },
    fallbacks=[]
)