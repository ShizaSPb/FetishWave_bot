import logging
from telegram import Update
from telegram.ext import ContextTypes

async def show_edit_profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню 'Изменить личные данные' (только кнопки)."""
    lang = context.user_data.get('lang', 'ru')
    await update_menu_message(
        update=update,
        context=context,
        text=LANGUAGES[lang]["edit_profile_title"],
        reply_markup=get_edit_profile_menu_keyboard(lang),
        is_query=True,
        parse_mode='HTML',
        menu_type='edit_profile_menu'
    )


from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data, notion
from bot.handlers import update_menu_message
from bot.utils.languages import LANGUAGES
from bot.handlers.menu import show_main_menu, show_personal_account
from bot.utils.keyboards import get_welcome_keyboard, get_main_menu_keyboard, get_edit_profile_menu_keyboard
from bot.utils.logger import log_action
from notion_client import Client
from config import NOTION_TOKEN, NOTION_DATABASE_ID


notion = Client(auth=NOTION_TOKEN)

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


async def handle_change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()  # Закрываем callback сразу

    # Мгновенное переключение языка в интерфейсе
    current_lang = context.user_data.get('lang', 'ru')
    new_lang = 'en' if current_lang == 'ru' else 'ru'
    context.user_data['lang'] = new_lang

    # Сначала обновляем интерфейс
    await show_personal_account(update, context)
    log_action("language_changed_ui", user_id, {"new_language": new_lang})

    # Затем запускаем фоновую задачу для Notion
    context.application.create_task(
        _update_language_in_notion(user_id, new_lang)
    )


async def _update_language_in_notion(user_id: int, new_lang: str):
    """Фоновая задача для обновления языка в Notion"""
    try:
        response = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            filter={"property": "Telegram ID", "number": {"equals": user_id}}
        )

        if response["results"]:
            page_id = response["results"][0]["id"]
            notion.pages.update(
                page_id=page_id,
                properties={"Language": {"select": {"name": new_lang}}}
            )
            log_action("notion_language_updated", user_id, {"new_language": new_lang})
    except Exception as e:
        logging.getLogger(__name__).error(f"Background Notion update failed: {e}", exc_info=True)
        log_action("notion_language_update_failed", user_id, {"error": str(e)})

handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(handle_personal_account, pattern="^menu_personal_account$"),
    CallbackQueryHandler(handle_change_language, pattern="^personal_change_lang$"),
    CallbackQueryHandler(show_edit_profile_menu, pattern="^personal_edit$"),
    CallbackQueryHandler(handle_personal_account, pattern="^personal_"),
]