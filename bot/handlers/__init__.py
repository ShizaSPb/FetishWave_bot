# Упростим импорты, убрав возможные циклические зависимости
from .start import handler as start_handler
from .view_data import handler as view_data_handler
from .callback import handlers as callback_handlers

# Импорт ConversationHandler перенесём в конец
def get_handlers():
    from .register import register_conversation_handler
    from .menu import handlers as menu_handlers
    return [
        start_handler,
        view_data_handler,
        *callback_handlers,
        *menu_handlers,
        register_conversation_handler
    ]

handlers = get_handlers()