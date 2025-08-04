import logging

from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from bot.data.webinar_descriptions import WEBINAR_DESCRIPTIONS
from bot.handlers.shared import update_menu_message
from bot.utils.languages import LANGUAGES
from bot.data.descriptions import DESCRIPTIONS
from bot.utils.keyboards import (
    get_payment_methods_keyboard,
    get_back_to_payment_methods_keyboard,
    get_hypno_payment_keyboard,
    get_back_to_hypno_payment_keyboard,
    get_femdom_payment_keyboard,
    get_back_to_femdom_payment_keyboard,
    get_back_to_consultation_payment_keyboard,
    get_online_session_payment_keyboard, get_back_to_menu_keyboard, get_back_to_currency_selection_keyboard
)
from bot.utils.logger import log_action

logger = logging.getLogger(__name__)

# Общие обработчики платежей
async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("payment_methods_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.replace("payment_methods_", "")

        context.user_data['current_webinar'] = webinar_id

        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["choose_payment"],
            reply_markup=get_payment_methods_keyboard(lang, webinar_id),
            is_query=True,
            parse_mode='HTML'
        )
        log_action("payment_methods_shown", user_id, {"webinar_id": webinar_id})

    except Exception as e:
        log_action("payment_methods_error", user_id, {"webinar_id": webinar_id, "error": str(e)})
        raise

async def show_consultation_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("consultation_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, currency, consultation_type = query.data.split(":")

        description = DESCRIPTIONS[lang][f"consultation_{consultation_type}_desc"]
        payment_details = {
            "rub": DESCRIPTIONS[lang]["payment_rub_details"],
            "crypto": DESCRIPTIONS[lang]["payment_crypto_details"],
            "eur": DESCRIPTIONS[lang]["payment_eur_details"]
        }[currency]

        await query.edit_message_text(
            text=f"{description}\n\n{payment_details}",
            reply_markup=get_back_to_consultation_payment_keyboard(lang, consultation_type),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("consultation_payment_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_consultation_payment: {e}")

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
            text=DESCRIPTIONS[lang]["payment_rub_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("rub_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("rub_payment_error", user_id, {"webinar_id": webinar_id, "error": str(e)})
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
            text=DESCRIPTIONS[lang]["payment_crypto_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("crypto_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("crypto_payment_error", user_id, {"webinar_id": webinar_id, "error": str(e)})
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
            text=DESCRIPTIONS[lang]["payment_eur_details"],
            reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
            parse_mode='HTML'
        )
        log_action("eur_payment_shown", user_id, {"webinar_id": webinar_id})
    except Exception as e:
        log_action("eur_payment_error", user_id, {"webinar_id": webinar_id, "error": str(e)})
        logger.error(f"Error in show_eur_payment: {e}", exc_info=True)
        raise

# Hypno payment handlers
async def show_hypno_rub_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("hypno_rub_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_hypno_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} в рублях</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_rub_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
        log_action("hypno_rub_payment_shown", user_id, {"part": part})
    except Exception as e:
        log_action("hypno_rub_payment_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_hypno_rub_payment: {e}", exc_info=True)
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def show_hypno_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("hypno_crypto_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_hypno_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} криптовалютой</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_crypto_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in show_hypno_crypto_payment: {e}")
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def show_hypno_eur_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("hypno_eur_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_hypno_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} в евро</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_eur_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in show_hypno_eur_payment: {e}")
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def back_to_hypno_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.replace("hypno_back_to_payment_", "")

        description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
            f"webinar_hypno_part_{part}",
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
        logger.error(f"Error in back_to_hypno_payment: {e}")
        await query.answer("⚠️ Ошибка при возврате")

# Femdom payment handlers
async def show_femdom_rub_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("femdom_rub_payment_open", user_id)
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_femdom_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} в рублях</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_rub_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_femdom_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("femdom_rub_payment_error", user_id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def show_femdom_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("femdom_crypto_payment_open", user_id)
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_femdom_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} криптовалютой</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_crypto_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_femdom_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in show_femdom_crypto_payment: {e}")
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def show_femdom_eur_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("femdom_eur_payment_open", user_id)
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        _, _, part = query.data.split(":")
        context.user_data['current_femdom_part'] = part

        payment_text = (
            f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']} в евро</b>\n\n"
            f"{DESCRIPTIONS[lang]['payment_eur_details']}"
        )

        await query.edit_message_text(
            text=payment_text,
            reply_markup=get_back_to_femdom_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in show_femdom_eur_payment: {e}")
        await query.answer("⚠️ Ошибка при загрузке реквизитов")

async def back_to_femdom_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.replace("femdom_back_to_payment_", "")

        description = WEBINAR_DESCRIPTIONS.get(lang, {}).get(
            f"webinar_femdom_part_{part}",
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
        logger.error(f"Error in back_to_femdom_payment: {e}")
        await query.answer("⚠️ Ошибка при возврате")

async def show_online_session_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("online_session_payment_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["choose_payment"],
            reply_markup=get_online_session_payment_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("online_session_payment_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_online_session_payment: {e}")


async def handle_online_session_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        currency = query.data.split(":")[1]  # rub/crypto/eur

        payment_details = {
            "rub": DESCRIPTIONS[lang]["payment_rub_details"],
            "crypto": DESCRIPTIONS[lang]["payment_crypto_details"],
            "eur": DESCRIPTIONS[lang]["payment_eur_details"]
        }[currency]

        await query.edit_message_text(
            text=f"💳 <b>{LANGUAGES[lang]['online_session']}</b>\n\n{payment_details}",
            reply_markup=get_back_to_currency_selection_keyboard(lang),  # Используем новую клавиатуру
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Error in handle_online_session_payment: {e}")
        await query.answer("⚠️ Ошибка при загрузке реквизитов")


async def back_to_currency_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=LANGUAGES[lang]["choose_payment"],
            reply_markup=get_online_session_payment_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in back_to_currency_selection: {e}")
        await query.answer("⚠️ Ошибка при возврате")

handlers = [
    # Common payments
    CallbackQueryHandler(show_payment_methods, pattern="^payment_methods_"),
    CallbackQueryHandler(show_rub_payment, pattern="^pay_rub_"),
    CallbackQueryHandler(show_crypto_payment, pattern="^pay_crypto_"),
    CallbackQueryHandler(show_eur_payment, pattern="^pay_eur_"),
    CallbackQueryHandler(show_consultation_payment, pattern="^consultation_pay:"),

    # Hypno payments
    CallbackQueryHandler(show_hypno_rub_payment, pattern="^hypno_pay:rub:"),
    CallbackQueryHandler(show_hypno_crypto_payment, pattern="^hypno_pay:crypto:"),
    CallbackQueryHandler(show_hypno_eur_payment, pattern="^hypno_pay:eur:"),
    CallbackQueryHandler(back_to_hypno_payment, pattern="^hypno_back_to_payment_"),

    # Femdom payments
    CallbackQueryHandler(show_femdom_rub_payment, pattern="^femdom_pay:rub:"),
    CallbackQueryHandler(show_femdom_crypto_payment, pattern="^femdom_pay:crypto:"),
    CallbackQueryHandler(show_femdom_eur_payment, pattern="^femdom_pay:eur:"),
    CallbackQueryHandler(back_to_femdom_payment, pattern="^femdom_back_to_payment_"),

    # Session payments
    CallbackQueryHandler(handle_online_session_payment, pattern="^online_session_payment:rub$"),
    CallbackQueryHandler(handle_online_session_payment, pattern="^online_session_payment:crypto$"),
    CallbackQueryHandler(handle_online_session_payment, pattern="^online_session_payment:eur$"),
    CallbackQueryHandler(back_to_currency_selection, pattern="^online_session_payment$"),
]