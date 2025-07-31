from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.handlers.menu import show_main_menu


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]
    context.user_data["lang"] = lang

    # Для теста сразу показываем главное меню
    await show_main_menu(update, context)


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu(update, context)


# Обработчики
handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$")
]