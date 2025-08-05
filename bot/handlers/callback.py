from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data
from bot.handlers import update_menu_message
from bot.utils.languages import LANGUAGES
from bot.handlers.menu import show_main_menu, show_personal_account
from bot.utils.keyboards import get_welcome_keyboard, get_main_menu_keyboard
from bot.utils.logger import log_action


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()

    lang = query.data.split("_")[-1]
    log_action("language_selected", user_id, {"language": lang})

    context.user_data["lang"] = lang
    user_data = await get_user_data(user_id)

    if user_data and user_data.get("status") == "Зарегистрирован":
        log_action("user_authenticated", user_id)
        context.user_data['registered'] = True
        await show_main_menu(update, context)
    else:
        log_action("user_not_authenticated", user_id)
        await query.edit_message_text(
            text=LANGUAGES[lang]["welcome"],
            reply_markup=get_welcome_keyboard(lang)
        )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("main_menu_request", user_id)

    try:
        query = update.callback_query
        await query.answer()

        # Убедимся, что язык установлен
        if 'lang' not in context.user_data:
            context.user_data['lang'] = 'ru'

        await show_main_menu(update, context)
        log_action("main_menu_shown", user_id)
    except Exception as e:
        log_action("main_menu_error", user_id, {"error": str(e)})
        # Пытаемся показать меню заново
        lang = context.user_data.get('lang', 'ru')
        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["main_menu"],
            reply_markup=get_main_menu_keyboard(lang),
            is_query=True,
            menu_type='main'
        )

async def handle_personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("personal_account_request", user_id)

    try:
        query = update.callback_query
        await query.answer()
        await show_personal_account(update, context)
    except Exception as e:
        log_action("personal_account_error", user_id, {"error": str(e)})

handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(handle_personal_account, pattern="^menu_personal_account$"),
    CallbackQueryHandler(handle_personal_account, pattern="^personal_"),
]