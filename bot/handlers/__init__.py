from .cabinet_products import handlers as cabinet_products_handlers
from .menu import handlers as menu_handlers
from .shared import update_menu_message
from .start import handler as start_handler
from .callback import handlers as callback_handlers
from .view_data import view_data_handler
from .registration import register_conversation_handler
from .menu import handlers as menu_handlers, show_main_menu, show_products_menu, show_consultations_menu, \
    show_mentoring_menu, show_page_audit_menu, show_session_menu
from .webinars import handlers as webinars_handlers, show_webinars_menu
from .payments import handlers as payments_handlers, handle_document
from bot.utils.logger import log_action
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from .admin_payments import handlers as admin_payments_handlers, remember_pending_payment
from .cabinet_products import handlers as cabinet_products_handlers
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.languages import LANGUAGES




async def block_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    log_action("invalid_text_input", user_id, {"text": update.message.text[:100]})

    if not context.user_data.get('registration_state'):
        try:
            await update.message.delete()

            current_menu_id = context.user_data.get('last_menu_message_id')
            last_menu_type = context.user_data.get('last_menu_type', 'main')  # Добавляем отслеживание типа меню

            if current_menu_id:
                try:
                    # Получаем текущее меню из контекста
                    menu_handler = {
                        'main': show_main_menu,
                        'products': show_products_menu,
                        'consultations': show_consultations_menu,
                        'mentoring': show_mentoring_menu,
                        'page_audit': show_page_audit_menu,
                        'webinars': show_webinars_menu,
                        'session': show_session_menu,
                        # Добавьте другие типы меню по необходимости
                    }.get(last_menu_type, show_main_menu)

                    await menu_handler(update, context)
                    log_action("menu_refreshed", user_id, {"menu_type": last_menu_type})
                    return
                except Exception as e:
                    log_action("menu_restore_failed", user_id, {
                        "error": str(e),
                        "menu_type": last_menu_type
                    })
                    pass

            # Если не удалось восстановить меню, показываем главное
            await show_main_menu(update, context)

        except Exception as e:
            log_action("text_input_handling_failed", user_id, {"error": str(e)})
            await show_main_menu(update, context)

def get_personal_account_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]["edit_profile"],      callback_data="personal_edit")],
        [InlineKeyboardButton(LANGUAGES[lang]["change_language"],   callback_data="personal_change_lang")],
        [InlineKeyboardButton(LANGUAGES[lang]["my_purchases"],      callback_data="cab:products")],  # <-- ВАЖНО: cab:products
        [InlineKeyboardButton(LANGUAGES[lang]["donate"],            callback_data="menu_donate")],
        [InlineKeyboardButton(LANGUAGES[lang]["back"],              callback_data="main_menu")]
    ])

def get_handlers():
    return [
        *cabinet_products_handlers,
        start_handler,
        view_data_handler,
        *callback_handlers,
        *admin_payments_handlers,
        *menu_handlers,
        *webinars_handlers,
        *payments_handlers,
        register_conversation_handler,
        MessageHandler(filters.TEXT & ~filters.COMMAND, block_text_input),
        MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document),
    ]


handlers = get_handlers()