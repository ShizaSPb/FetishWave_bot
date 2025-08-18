
# bot/middleware/audit.py
from telegram import Update
from telegram.ext import TypeHandler, ContextTypes
from bot.services.actions import log_action

async def audit_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    u = update.effective_user
    c = update.effective_chat
    uid = u.id if u else None
    uname = u.username if u else None
    chat_id = c.id if c else None

    # Log commands
    if update.message and update.message.text:
        txt = update.message.text.strip()
        if txt.startswith("/"):
            log_action("cmd", user_id=uid, username=uname, chat_id=chat_id, text=txt)

    # Log callback queries
    if update.callback_query:
        data = (update.callback_query.data or "")[:200]
        log_action("callback", user_id=uid, username=uname, chat_id=chat_id, data=data)

# export handler to be added in main with low group (runs before others)
audit_handler = TypeHandler(Update, audit_update, block=False)
