from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.handlers.shared import get_user_language


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]  # Получаем 'ru' или 'en'
    context.user_data["lang"] = lang

    # Редактируем исходное сообщение, заменяя кнопки выбора языка на кнопку регистрации
    keyboard = [[InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]]
    await query.edit_message_text(
        text=LANGUAGES[lang]["welcome"],  # "Добро пожаловать!"
        reply_markup=InlineKeyboardMarkup(keyboard)  # Кнопка "Зарегистрироваться"
    )


async def start_register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = get_user_language(context)
    await query.message.reply_text(LANGUAGES[lang]["enter_name"])

    from bot.handlers.register import NAME
    return NAME


handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(start_register_callback, pattern="^start_register$")
]