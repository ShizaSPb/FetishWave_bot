from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data
from bot.utils.languages import LANGUAGES
from bot.handlers.menu import show_main_menu
from bot.utils.keyboards import get_welcome_keyboard

async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]
    context.user_data["lang"] = lang

    # Проверяем регистрацию
    user_data = await get_user_data(update.effective_user.id)
    if user_data and user_data.get("status") == "Зарегистрирован":
        context.user_data['registered'] = True
        await show_main_menu(update, context)
    else:
        await query.edit_message_text(
            text=LANGUAGES[lang]["welcome"],
            reply_markup=get_welcome_keyboard(lang)
        )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await show_main_menu(update, context)

handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$")
]