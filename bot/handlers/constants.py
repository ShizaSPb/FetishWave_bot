from telegram.ext import filters
# Константы для состояний ConversationHandler
NAME, EMAIL = range(2)
TEXT_FILTER = filters.TEXT & ~filters.COMMAND