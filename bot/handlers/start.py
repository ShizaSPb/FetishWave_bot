from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from bot.handlers.shared import send_language_keyboard

async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    await send_language_keyboard(update)

handler = CommandHandler('start', start)