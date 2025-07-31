from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data
from bot.utils.languages import LANGUAGES
from bot.handlers.menu import show_main_menu


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]
    context.user_data["lang"] = lang

    # Проверяем регистрацию пользователя
    user_data = await get_user_data(update.effective_user.id)

    if user_data and user_data.get("status") == "Зарегистрирован":
        # Если зарегистрирован - сразу в главное меню
        await show_main_menu(update, context)
    else:
        # Если не зарегистрирован - показываем кнопку регистрации
        await query.edit_message_text(
            text=LANGUAGES[lang]["welcome"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
            ])
        )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get('lang', 'ru')
    await query.edit_message_text(
        text=LANGUAGES[lang]["welcome"],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
        ])
    )


# Добавьте в список обработчиков
handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$")
]