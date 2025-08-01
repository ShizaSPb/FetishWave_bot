import re
from datetime import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from bot.database.notion_db import add_user_to_notion, get_user_data
from bot.handlers.shared import get_user_language
from bot.utils.languages import LANGUAGES

logger = logging.getLogger(__name__)
NAME, EMAIL = range(2)


async def start_register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        # Проверяем, не зарегистрирован ли уже пользователь
        existing_user = await get_user_data(update.effective_user.id)
        if existing_user:
            lang = context.user_data.get('lang', 'ru')
            await query.edit_message_text(
                LANGUAGES[lang]["already_registered"],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        LANGUAGES[lang]["menu_button"],
                        callback_data="main_menu"
                    )]
                ])
            )
            return ConversationHandler.END

        if 'lang' not in context.user_data:
            raise ValueError("Language not selected")

        context.user_data.update({
            'telegram_id': update.effective_user.id,
            'username': update.effective_user.username or "",
            'language': context.user_data['lang'],
            'messages_to_delete': [query.message.message_id],
            'status': "Не зарегистрирован"  # Временный статус
        })

        await query.edit_message_text(LANGUAGES[context.user_data['lang']]["enter_name"])
        return NAME

    except Exception as e:
        logger.error(f"Registration start failed: {str(e)}", exc_info=True)
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text("❌ Ошибка начала регистрации")
        return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            raise ValueError("Invalid name input")

        context.user_data['name'] = update.message.text.strip()
        context.user_data.setdefault('messages_to_delete', []).append(update.message.message_id)

        lang = get_user_language(context)
        msg = await update.message.reply_text(LANGUAGES[lang]["enter_email"])
        context.user_data['messages_to_delete'].append(msg.message_id)

        return EMAIL
    except Exception as e:
        logger.error(f"Name input error: {e}", exc_info=True)
        await handle_registration_failure(update, context)
        return ConversationHandler.END


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        required_keys = ['name', 'telegram_id', 'username', 'language']
        if not all(key in context.user_data for key in required_keys):
            raise KeyError("Missing registration data")

        if not update.message or not update.message.text:
            raise ValueError("Invalid email input")

        email = update.message.text.strip()
        context.user_data.setdefault('messages_to_delete', []).append(update.message.message_id)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")

        # Обновляем статус перед сохранением
        context.user_data['status'] = "Зарегистрирован"

        # Создаем запись в Notion
        await add_user_to_notion({
            "telegram_id": context.user_data['telegram_id'],
            "username": context.user_data['username'],
            "language": context.user_data['language'],
            "name": context.user_data['name'],
            "email": email,
            "status": context.user_data['status'],
            "reg_date": datetime.now().isoformat()
        })

        # Устанавливаем флаг регистрации
        context.user_data['registered'] = True

        # Очищаем сообщения перед переходом в меню
        await cleanup_messages(context, update.effective_chat.id)

        # Переходим в главное меню
        from bot.handlers.menu import show_main_menu
        await show_main_menu(update, context)

        return ConversationHandler.END

    except ValueError as e:
        logger.warning(f"Validation error: {e}", exc_info=True)
        error_msg = await update.message.reply_text("❌ Неверный формат email. Попробуйте снова:")
        context.user_data.setdefault('messages_to_delete', []).append(error_msg.message_id)
        return EMAIL
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        await handle_registration_failure(update, context)
        return ConversationHandler.END


async def cleanup_messages(context, chat_id):
    """Удаляет все сообщения из списка messages_to_delete"""
    if 'messages_to_delete' not in context.user_data:
        return

    for msg_id in context.user_data['messages_to_delete']:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение {msg_id}: {e}")

    # Очищаем список после удаления
    del context.user_data['messages_to_delete']



async def handle_registration_failure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await cleanup_messages(context, update.effective_chat.id)
        if update.message:
            await update.message.reply_text(
                "❌ Ошибка регистрации. Начните заново командой /start"
            )
    except Exception as e:
        logger.error(f"Failure handling error: {e}", exc_info=True)


register_conversation_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_register_callback, pattern="^start_register$")
    ],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)]
    },
    fallbacks=[],
    per_message=False
)