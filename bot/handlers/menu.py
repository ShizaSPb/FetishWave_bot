from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = context.user_data.get('lang', 'ru')

    # Простое меню с одной кнопкой для теста
    keyboard = [
        [InlineKeyboardButton("🎉 Ура!", callback_data="test_hooray")],
        [InlineKeyboardButton(LANGUAGES[lang]["register"], callback_data="start_register")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.answer()
        await query.edit_message_text(
            text="Тестовое меню",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            text="Тестовое меню",
            reply_markup=reply_markup
        )


async def test_hooray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        text="🎉 Ура! Тест пройден успешно!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Назад", callback_data="menu_main")]
        ])
    )


# Регистрация обработчиков
handlers = [
    CallbackQueryHandler(show_main_menu, pattern="^menu_main$"),
    CallbackQueryHandler(test_hooray, pattern="^test_hooray$")
]