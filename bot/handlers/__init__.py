from .start import handler as start_handler
from .callback import handlers as callback_handlers
from .view_data import view_data_handler
from .registration import register_conversation_handler
from .menu import handlers as menu_handlers
from .webinars import handlers as webinars_handlers
from .payments import handlers as payments_handlers

def get_handlers():
    return [
        start_handler,
        view_data_handler,
        *callback_handlers,
        *menu_handlers,
        *webinars_handlers,
        *payments_handlers,
        register_conversation_handler
    ]

handlers = get_handlers()