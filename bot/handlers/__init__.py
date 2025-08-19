
# bot/handlers/__init__.py — реестр хендлеров (быстрые ПЕРВЫМИ)
from telegram.ext import MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# Импорт быстрых хендлеров
from .payments_fast_ack import handlers as fast_ack_handlers

# Остальные модули проекта
from .cabinet_products import handlers as cabinet_products_handlers
from .menu import (handlers as menu_handlers, show_main_menu, show_products_menu, show_consultations_menu,
                   show_mentoring_menu, show_page_audit_menu, show_session_menu)
from .shared import update_menu_message
from .start import handler as start_handler
from .callback import handlers as callback_handlers
from .view_data import view_data_handler
from .registration import register_conversation_handler
from .payments import handlers as payments_handlers, handle_document
from .admin_payments import handlers as admin_payments_handlers
from .webinars import handlers as webinars_handlers, show_webinars_menu

async def block_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text if update.message else ''
    if not text:
        return
    try:
        await update.message.delete()
        current_menu_id = context.user_data.get('last_menu_message_id')
        last_menu_type = context.user_data.get('last_menu_type', 'main')
        if current_menu_id:
            menu_handler = {
                'main': show_main_menu,
                'products': show_products_menu,
                'consultations': show_consultations_menu,
                'mentoring': show_mentoring_menu,
                'page_audit': show_page_audit_menu,
                'session': show_session_menu,
                'webinars': show_webinars_menu,
            }.get(last_menu_type, show_main_menu)
            await menu_handler(update, context, cleanup_previous=False)
    except Exception:
        pass

def get_handlers():
    return [
        # ВАЖНО: быстрые — первыми, чтобы стопорить цепочку
        *fast_ack_handlers,

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
        # Fallback обработчик документов — в самом конце
        MessageHandler(filters.Document.ALL | filters.PHOTO, handle_document),
    ]

handlers = get_handlers()
