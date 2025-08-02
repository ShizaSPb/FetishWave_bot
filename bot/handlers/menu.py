import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.utils.languages import LANGUAGES
from bot.database.notion_db import get_user_data
from bot.data.webinar_descriptions import WEBINAR_DESCRIPTIONS
from bot.utils.keyboards import (
    get_main_menu_keyboard,
    get_products_menu_keyboard,
    get_webinars_menu_keyboard,
    get_webinar_details_keyboard,
    get_consultations_menu_keyboard,
    get_mentoring_menu_keyboard,
    get_page_audit_menu_keyboard,
    get_private_channel_menu_keyboard,
    get_payment_methods_keyboard,
    get_back_to_payment_methods_keyboard,
    get_welcome_keyboard
)
from bot.utils.logger import log_action

logger = logging.getLogger(__name__)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("main_menu_open", user_id)

    try:
        query = update.callback_query
        if query:
            await query.answer()

        lang = context.user_data.get('lang', 'ru')
        is_registered = context.user_data.get('registered') or await check_registration(user_id)

        if is_registered:
            context.user_data['registered'] = True
            reply_markup = get_main_menu_keyboard(lang)
            log_action("main_menu_shown", user_id, {"status": "registered"})

            if query:
                await query.edit_message_text(
                    text=LANGUAGES[lang]["main_menu"],
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text=LANGUAGES[lang]["main_menu"],
                    reply_markup=reply_markup
                )
        else:
            log_action("main_menu_blocked", user_id, {"reason": "unregistered"})
            if query:
                await query.edit_message_text(
                    text=LANGUAGES[lang]["registration_required"],
                    reply_markup=get_welcome_keyboard(lang)
                )
            else:
                await update.message.reply_text(
                    text=LANGUAGES[lang]["registration_required"],
                    reply_markup=get_welcome_keyboard(lang)
                )
    except Exception as e:
        log_action("menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_main_menu: {e}", exc_info=True)
        raise


async def check_registration(user_id: int) -> bool:
    try:
        log_action("check_registration", user_id)
        user_data = await get_user_data(user_id)
        return user_data and user_data.get("status") == "Зарегистрирован"
    except Exception as e:
        log_action("check_registration_failed", user_id, {"error": str(e)})
        logger.error(f"Error in check_registration: {e}", exc_info=True)
        return False


async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("products_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["products"],
            reply_markup=get_products_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("products_menu_shown", user_id)
    except Exception as e:
        log_action("products_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_products_menu: {e}", exc_info=True)
        raise


async def show_webinars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("webinars_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["webinars_title"],
            reply_markup=get_webinars_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("webinars_menu_shown", user_id)
    except Exception as e:
        log_action("webinars_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_webinars_menu: {e}", exc_info=True)
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

        await query.edit_message_text(
            text=description,
            reply_markup=get_webinar_details_keyboard(lang, full_webinar_id),
            parse_mode='HTML'
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


async def show_consultations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("consultations_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["consultations_description"],
            reply_markup=get_consultations_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("consultations_menu_shown", user_id)
    except Exception as e:
        log_action("consultations_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_consultations_menu: {e}", exc_info=True)
        raise


async def show_mentoring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("mentoring_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["mentoring_description"],
            reply_markup=get_mentoring_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("mentoring_menu_shown", user_id)
    except Exception as e:
        log_action("mentoring_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_mentoring_menu: {e}", exc_info=True)
        raise


async def show_page_audit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("page_audit_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["page_audit_description"],
            reply_markup=get_page_audit_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("page_audit_menu_shown", user_id)
    except Exception as e:
        log_action("page_audit_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_page_audit_menu: {e}", exc_info=True)
        raise


async def show_private_channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("private_channel_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["private_channel_description"],
            reply_markup=get_private_channel_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("private_channel_menu_shown", user_id)
    except Exception as e:
        log_action("private_channel_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_private_channel_menu: {e}", exc_info=True)
        raise


async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("payment_methods_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.replace("payment_methods_", "")

        context.user_data['current_webinar'] = webinar_id

        await query.edit_message_text(
            text=LANGUAGES[lang]["choose_payment"],
            reply_markup=get_payment_methods_keyboard(lang, webinar_id),
            parse_mode='HTML'
        )
        log_action("payment_methods_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("payment_methods_error", user_id, {
            "webinar_id": webinar_id,
            "error": str(e)
        })
        logger.error(f"Error in show_payment_methods: {e}", exc_info=True)
        raise


async def show_rub_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("rub_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.replace("pay_rub_", "")

        context.user_data['current_webinar'] = webinar_id

        await query.edit_message_text(
            text=LANGUAGES[lang]["payment_rub_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("rub_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("rub_payment_error", user_id, {
            "webinar_id": webinar_id,
            "error": str(e)
        })
        logger.error(f"Error in show_rub_payment: {e}", exc_info=True)
        raise


async def show_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("crypto_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.replace("pay_crypto_", "")

        context.user_data['current_webinar'] = webinar_id

        await query.edit_message_text(
            text=LANGUAGES[lang]["payment_crypto_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("crypto_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("crypto_payment_error", user_id, {
            "webinar_id": webinar_id,
            "error": str(e)
        })
        logger.error(f"Error in show_crypto_payment: {e}", exc_info=True)
        raise


async def show_eur_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("eur_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.replace("pay_eur_", "")

        context.user_data['current_webinar'] = webinar_id

        await query.edit_message_text(
            text=LANGUAGES[lang]["payment_eur_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("eur_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("eur_payment_error", user_id, {
            "webinar_id": webinar_id,
            "error": str(e)
        })
        logger.error(f"Error in show_eur_payment: {e}", exc_info=True)
        raise


handlers = [
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_details_"),
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_"),
    CallbackQueryHandler(show_main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(show_products_menu, pattern="^menu_products$"),
    CallbackQueryHandler(show_webinars_menu, pattern="^menu_webinars$"),
    CallbackQueryHandler(show_consultations_menu, pattern="^menu_consultations$"),
    CallbackQueryHandler(show_mentoring_menu, pattern="^menu_mentoring$"),
    CallbackQueryHandler(show_page_audit_menu, pattern="^menu_page_audit$"),
    CallbackQueryHandler(show_private_channel_menu, pattern="^menu_private_channel$"),
    CallbackQueryHandler(show_payment_methods, pattern="^payment_methods_"),
    CallbackQueryHandler(show_rub_payment, pattern="^pay_rub_"),
    CallbackQueryHandler(show_crypto_payment, pattern="^pay_crypto_"),
    CallbackQueryHandler(show_eur_payment, pattern="^pay_eur_"),
]