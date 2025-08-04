import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot.handlers.shared import update_menu_message
from bot.utils.languages import LANGUAGES
from bot.data.webinar_descriptions import WEBINAR_DESCRIPTIONS
from bot.data.descriptions import DESCRIPTIONS
from bot.utils.keyboards import (
    get_webinars_menu_keyboard,
    get_webinar_details_keyboard,
    get_hypno_webinar_keyboard,
    get_hypno_payment_keyboard,
    get_back_to_hypno_payment_keyboard,
    get_femdom_webinar_keyboard,
    get_femdom_payment_keyboard,
    get_back_to_femdom_payment_keyboard
)
from bot.utils.logger import log_action

logger = logging.getLogger(__name__)


async def show_webinars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("webinars_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["webinars_title"],
            reply_markup=get_webinars_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='webinars'  # Добавлено
        )
        log_action("webinars_menu_shown", user_id)

    except Exception as e:
        log_action("webinars_menu_error", user_id, {"error": str(e)})
        raise


async def show_webinar_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("webinar_details_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        webinar_id = query.data.replace("webinar_details_", "").replace("webinar_", "")
        full_webinar_id = f"webinar_{webinar_id}"

        description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
            full_webinar_id,
            LANGUAGES[lang].get("default_description", "")
        )

        await update_menu_message(
            update=update,
            context=context,
            text=description,
            reply_markup=get_webinar_details_keyboard(lang, full_webinar_id),
            is_query=True,
            parse_mode='HTML',
            menu_type='webinars'  # Добавлено
        )
        log_action("webinar_details_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("webinar_details_error", user_id, {
            "webinar_id": webinar_id,
            "error": str(e)
        })
        logger.error(f"Error showing webinar details: {e}", exc_info=True)
        await query.edit_message_text(
            text="⚠️ Произошла ошибка при загрузке описания",
            reply_markup=get_webinar_details_keyboard(lang, full_webinar_id)
        )


async def show_hypno_webinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        webinar_text = WEBINAR_DESCRIPTIONS.get(lang, {}).get("webinar_hypno")

        await update_menu_message(
            update=update,
            context=context,
            text=webinar_text,
            reply_markup=get_hypno_webinar_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='webinars'  # Добавлено
        )
        log_action("hypno_webinar_shown", user_id)
    except Exception as e:
        log_action("hypno_webinar_error", user_id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при обновлении")


async def handle_hypno_part_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.split(":")[1]  # "1", "2" или "both"

        description_key = f"webinar_hypno_part_{part}"
        description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
            description_key,
            f"Описание части {part} не найдено"
        )

        message_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']}</b>\n\n"
            f"{description}\n\n"
            "Выберите способ оплаты:"
        )

        await query.edit_message_text(
            text=message_text,
            reply_markup=get_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in handle_hypno_part_selection: {e}")
        await query.answer("⚠️ Ошибка при загрузке описания")


async def back_to_hypno_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_hypno_webinar(update, context)


async def back_to_webinars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_webinars_menu(update, context)


# Femdom webinar handlers
async def show_femdom_webinar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        webinar_text = WEBINAR_DESCRIPTIONS.get(lang, {}).get("webinar_femdom")

        await update_menu_message(
            update=update,
            context=context,
            text=webinar_text,
            reply_markup=get_femdom_webinar_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='webinars'  # Добавлено
        )
        log_action("femdom_webinar_shown", user_id)
    except Exception as e:
        log_action("femdom_webinar_error", user_id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при обновлении")


async def handle_femdom_part_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.split(":")[1]

        description_key = f"webinar_femdom_part_{part}"
        description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
            description_key,
            f"Описание части {part} не найдено"
        )

        message_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']}</b>\n\n"
            f"{description}\n\n"
            "Выберите способ оплаты:"
        )

        await query.edit_message_text(
            text=message_text,
            reply_markup=get_femdom_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in handle_femdom_part_selection: {e}")
        await query.answer("⚠️ Ошибка при загрузке описания")


async def back_to_femdom_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_femdom_webinar(update, context)


handlers = [
    # Webinars
    CallbackQueryHandler(show_webinars_menu, pattern="^menu_webinars$"),
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_details_"),
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_"),

    # Hypno
    CallbackQueryHandler(show_hypno_webinar, pattern="^hypno_webinar$"),
    CallbackQueryHandler(handle_hypno_part_selection, pattern="^hypno_part:"),
    CallbackQueryHandler(back_to_webinars, pattern="^back_to_webinars$"),
    CallbackQueryHandler(back_to_hypno_parts, pattern="^back_to_hypno_parts$"),

    # Femdom
    CallbackQueryHandler(show_femdom_webinar, pattern="^femdom_webinar$"),
    CallbackQueryHandler(handle_femdom_part_selection, pattern="^femdom_part:"),
    CallbackQueryHandler(back_to_femdom_parts, pattern="^back_to_femdom_parts$"),
]