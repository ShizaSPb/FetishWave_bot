from typing import Optional

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.utils.keyboards import get_language_keyboard
from bot.utils.logger import log_action


def get_user_language(context):
    return context.user_data.get("lang", "ru")

async def send_language_keyboard(update: Update):
    await update.message.reply_text(
        "Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
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


async def update_menu_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup: InlineKeyboardMarkup,
        is_query: bool = False,
        parse_mode: Optional[str] = None,
        menu_type: str = 'main',
        cleanup_previous: bool = False  # Новый параметр
) -> None:
    """Универсальная функция для управления меню"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Сохраняем тип текущего меню
    context.user_data['last_menu_type'] = menu_type

    try:
        # Удаляем предыдущее меню и файлы, если требуется
        if cleanup_previous and 'last_file_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=context.user_data['last_file_message_id']
                )
                del context.user_data['last_file_message_id']
            except Exception as e:
                log_action("file_deletion_failed", user_id, {"error": str(e)})

        # Отправляем новое меню
        if is_query and hasattr(update, 'callback_query'):
            try:
                await update.callback_query.edit_message_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                context.user_data['last_menu_message_id'] = update.callback_query.message.message_id
            except Exception as e:
                # Если не удалось отредактировать, отправляем новое сообщение
                message = await context.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                context.user_data['last_menu_message_id'] = message.message_id
        else:
            message = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            context.user_data['last_menu_message_id'] = message.message_id

        log_action("new_menu_sent", user_id, {"menu_type": menu_type})

    except Exception as e:
        log_action("menu_update_failed", user_id, {"error": str(e), "menu_type": menu_type})
        raise