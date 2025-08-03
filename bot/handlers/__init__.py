from .start import handler as start_handler
from .callback import handlers as callback_handlers
from .view_data import view_data_handler

def get_handlers():
    from .registration import register_conversation_handler
    from .menu import handlers as menu_handlers
    return [
        start_handler,
        view_data_handler,
        *callback_handlers,
        *menu_handlers,
        register_conversation_handler
    ]

handlers = get_handlers()