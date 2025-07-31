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

async def replace_previous_message(context, chat_id, message_id, new_text, reply_markup=None):
    """Универсальная функция для подмены сообщений"""
    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=new_text,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Ошибка при подмене сообщения: {e}")
        # Fallback - отправляем новое сообщение
        new_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=new_text,
            reply_markup=reply_markup
        )
        return new_msg.message_id
    return message_id