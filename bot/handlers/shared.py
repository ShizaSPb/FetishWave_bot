from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.utils.languages import LANGUAGES

def get_user_language(context):
    return context.user_data.get("lang", "ru")

async def send_language_keyboard(update):
    keyboard = [
        [InlineKeyboardButton(LANGUAGES["ru"]["language_name"], callback_data="set_lang_ru")],
        [InlineKeyboardButton(LANGUAGES["en"]["language_name"], callback_data="set_lang_en")]
    ]
    await update.message.reply_text(
        "Выберите язык / Choose language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )