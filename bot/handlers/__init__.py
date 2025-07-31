from .start import handler as start_handler
from .view_data import handler as view_data_handler
from .callback import handlers as callback_handlers
from .register import register_conversation_handler

handlers = [
    start_handler,
    view_data_handler,
    *callback_handlers,
    register_conversation_handler
]