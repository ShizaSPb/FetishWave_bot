from email_validator import validate_email, EmailNotValidError
import re
from datetime import datetime
import logging
from telegram import Update
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
from bot.utils.keyboards import get_already_registered_keyboard
from bot.services.actions import log_action

logger = logging.getLogger(__name__)
NAME, EMAIL = range(2)


async def start_register_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("register_started", user_id)

    try:
        query = update.callback_query
        await query.answer()

        existing_user = await get_user_data(user_id)
        if existing_user:
            log_action("register_attempt", user_id, {"status": "already_registered"})
            lang = context.user_data.get('lang', 'ru')
            await query.edit_message_text(
                LANGUAGES[lang]["already_registered"],
                reply_markup=get_already_registered_keyboard(lang)
            )
            return ConversationHandler.END

        if 'lang' not in context.user_data:
            raise ValueError(LANGUAGES[context.user_data.get('lang', 'ru')]["language_not_selected"])

        lang = context.user_data['lang']
        context.user_data.update({
            'telegram_id': user_id,
            'username': update.effective_user.username or "",
            'language': lang,
            'messages_to_delete': [query.message.message_id],
            'status': LANGUAGES[lang]["status_not_registered"]
        })

        await query.edit_message_text(LANGUAGES[lang]["enter_name"])
        log_action("register_name_requested", user_id)
        return NAME

    except Exception as e:
        lang = context.user_data.get('lang', 'ru')
        log_action("register_failed", user_id, {"error": str(e)})
        logger.error(f"Registration start failed: {str(e)}", exc_info=True)
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.reply_text(LANGUAGES[lang]["registration_start_error"])
        return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(context)

    try:
        if not update.message or not update.message.text:
            raise ValueError(LANGUAGES[lang]["invalid_name_input"])

        name = update.message.text.strip()
        log_action("register_name_input", user_id, {"raw_input": name})

        # Валидация имени
        if len(name) < 2:
            raise ValueError(LANGUAGES[lang]['name_too_short'])
        if len(name) > 30:
            raise ValueError(LANGUAGES[lang]['name_too_long'])
        if re.search(r'[0-9_!@#$%^&*(),.?":{}|<>]', name):
            raise ValueError(LANGUAGES[lang]['name_invalid_chars'])
        if re.search(r'(http|www|\.com|\.ru|\.net)', name, re.I):
            raise ValueError(LANGUAGES[lang]['name_suspicious'])
        if name.lower() in ['admin', 'support', 'test', 'user']:
            raise ValueError(LANGUAGES[lang]['name_generic'])

        context.user_data['name'] = name
        context.user_data.setdefault('messages_to_delete', []).append(update.message.message_id)

        msg = await update.message.reply_text(LANGUAGES[lang]["enter_email"])
        context.user_data['messages_to_delete'].append(msg.message_id)

        log_action("register_name_received", user_id, {"name": name})
        return EMAIL

    except ValueError as e:
        log_action("register_name_error", user_id, {
            "error": str(e),
            "raw_input": name,
            "normalized_input": name.strip()
        })
        error_msg = await update.message.reply_text(
            f"❌ {str(e)}\n{LANGUAGES[lang]['enter_name_again']}"
        )
        context.user_data.setdefault('messages_to_delete', []).append(error_msg.message_id)
        return NAME

    except Exception as e:
        log_action("register_name_error", user_id, {"error": str(e)})
        logger.error(f"Name input error: {e}", exc_info=True)
        await handle_registration_failure(update, context)
        return ConversationHandler.END


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(context)

    try:
        required_keys = ['name', 'telegram_id', 'username', 'language']
        if not all(key in context.user_data for key in required_keys):
            raise KeyError(LANGUAGES[lang]["missing_registration_data"])

        if not update.message or not update.message.text:
            raise ValueError(LANGUAGES[lang]["invalid_email_input"])

        email = update.message.text.strip()
        log_action("register_email_input", user_id, {"raw_input": email})
        context.user_data.setdefault('messages_to_delete', []).append(update.message.message_id)

        try:
            valid = validate_email(
                email,
                check_deliverability=True,
                allow_smtputf8=False,
                allow_empty_local=False
            )
            normalized_email = valid.normalized
        except EmailNotValidError as e:
            error_message = str(e)
            if "The domain name" in error_message and "does not exist" in error_message:
                error_message = LANGUAGES[lang]['email_domain_error']
            elif "There must be something after" in error_message:
                error_message = LANGUAGES[lang]['email_incomplete']
            else:
                error_message = LANGUAGES[lang]['email_invalid']

            log_action("register_email_error", user_id, {
                "error": error_message,
                "raw_input": email,
                "normalized_attempt": email.strip().lower()
            })

            error_msg = await update.message.reply_text(
                f"❌ {error_message}\n{LANGUAGES[lang]['enter_email_again']}"
            )
            context.user_data['messages_to_delete'].append(error_msg.message_id)
            return EMAIL

        context.user_data['email'] = normalized_email
        context.user_data['status'] = LANGUAGES[lang]["status_registered"]

        await add_user_to_notion({
            "telegram_id": context.user_data['telegram_id'],
            "username": context.user_data['username'],
            "language": context.user_data['language'],
            "name": context.user_data['name'],
            "email": normalized_email,
            "status": context.user_data['status'],
            "reg_date": datetime.now().isoformat()
        })

        context.user_data['registered'] = True
        await cleanup_messages(context, update.effective_chat.id)

        from bot.handlers.menu import show_main_menu
        await show_main_menu(update, context)

        log_action("register_success", user_id, {
            "email": normalized_email,
            "username": context.user_data['username']
        })
        return ConversationHandler.END

    except Exception as e:
        log_action("register_failed", user_id, {"error": str(e)})
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        await handle_registration_failure(update, context)
        return ConversationHandler.END


async def cleanup_messages(context, chat_id):
    if 'messages_to_delete' not in context.user_data:
        return

    for msg_id in context.user_data['messages_to_delete']:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            logger.warning(f"Failed to delete message {msg_id}: {e}")

    del context.user_data['messages_to_delete']


async def handle_registration_failure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(context)

    try:
        await cleanup_messages(context, update.effective_chat.id)
        if update.message:
            await update.message.reply_text(LANGUAGES[lang]["registration_failed"])
        log_action("register_cleanup_complete", user_id)
    except Exception as e:
        log_action("register_cleanup_failed", user_id, {"error": str(e)})
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