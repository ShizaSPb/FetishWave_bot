from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]
    context.user_data["lang"] = lang

    # Подменяем сообщение с кнопками выбора языка
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