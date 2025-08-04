from .shared import update_menu_message
from .start import handler as start_handler
from .callback import handlers as callback_handlers
from .view_data import view_data_handler
from .registration import register_conversation_handler
from .menu import handlers as menu_handlers
from .webinars import handlers as webinars_handlers
from .payments import handlers as payments_handlers
from bot.utils.keyboards import get_main_menu_keyboard
from bot.utils.logger import log_action
from bot.utils.languages import LANGUAGES
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters


async def block_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    log_action("invalid_text_input", user_id, {"text": update.message.text[:100]})

    if not context.user_data.get('registration_state'):
        try:
            await update.message.delete()

            current_menu_id = context.user_data.get('last_menu_message_id')

            if current_menu_id:
                try:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=current_menu_id,
                        text=LANGUAGES[lang]["main_menu"],
                        reply_markup=get_main_menu_keyboard(lang)
                    )
                    log_action("menu_refreshed", user_id)
                    return
                except Exception:
                    pass

            await update_menu_message(
                update=update,
                context=context,
                text=LANGUAGES[lang]["main_menu"],
                reply_markup=get_main_menu_keyboard(lang),
                is_query=False
            )

        except Exception as e:
            log_action("text_input_handling_failed", user_id, {"error": str(e)})


def get_handlers():
    return [
        start_handler,
        view_data_handler,
        *callback_handlers,
        *menu_handlers,
        *webinars_handlers,
        *payments_handlers,
        register_conversation_handler,
        MessageHandler(filters.TEXT & ~filters.COMMAND, block_text_input)
    ]


handlers = get_handlers()