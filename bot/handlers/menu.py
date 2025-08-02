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

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    lang = context.user_data.get('lang', 'ru')
    is_registered = context.user_data.get('registered') or await check_registration(update.effective_user.id)

    if is_registered:
        context.user_data['registered'] = True
        reply_markup = get_main_menu_keyboard(lang)

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

async def check_registration(user_id: int) -> bool:
    """Проверяет регистрацию в Notion"""
    user_data = await get_user_data(user_id)
    return user_data and user_data.get("status") == "Зарегистрирован"

async def show_products_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text=LANGUAGES[lang]["products"],
        reply_markup=get_products_menu_keyboard(lang),
        parse_mode = 'HTML'
    )

async def show_webinars_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text="🎓 <b>Доступные вебинары:</b>\n\nВыберите интересующий вас вебинар:",
        reply_markup=get_webinars_menu_keyboard(lang),
        parse_mode='HTML'
    )


async def show_webinar_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    # Обрабатываем оба формата callback_data
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

async def show_consultations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text=LANGUAGES[lang]["consultations_description"],
        reply_markup=get_consultations_menu_keyboard(lang),
        parse_mode = 'HTML'
    )

async def show_mentoring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text=LANGUAGES[lang]["mentoring_description"],
        reply_markup=get_mentoring_menu_keyboard(lang)
    )

async def show_page_audit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text=LANGUAGES[lang]["page_audit_description"],
        reply_markup=get_page_audit_menu_keyboard(lang),
        parse_mode = 'HTML'
    )

async def show_private_channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    await query.edit_message_text(
        text=LANGUAGES[lang]["private_channel_description"],
        reply_markup=get_private_channel_menu_keyboard(lang),
        parse_mode = 'HTML'
    )

async def show_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data.replace("payment_methods_", "")

    # Сохраняем webinar_id в контексте для возможного использования
    context.user_data['current_webinar'] = webinar_id

    await query.edit_message_text(
        text=LANGUAGES[lang]["choose_payment"],
        reply_markup=get_payment_methods_keyboard(lang, webinar_id),
        parse_mode = 'HTML'
    )


async def show_rub_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data.replace("pay_rub_", "")

    # Сохраняем текущий вебинар в контексте
    context.user_data['current_webinar'] = webinar_id

    await query.edit_message_text(
        text=LANGUAGES[lang]["payment_rub_details"],
        reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
        parse_mode='HTML'
    )


async def show_crypto_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data.replace("pay_crypto_", "")

    # Сохраняем текущий вебинар в контексте
    context.user_data['current_webinar'] = webinar_id

    await query.edit_message_text(
        text=LANGUAGES[lang]["payment_crypto_details"],
        reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
        parse_mode='HTML'
    )


async def show_eur_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    webinar_id = query.data.replace("pay_eur_", "")

    # Сохраняем текущий вебинар в контексте
    context.user_data['current_webinar'] = webinar_id

    await query.edit_message_text(
        text=LANGUAGES[lang]["payment_eur_details"],
        reply_markup=get_back_to_payment_methods_keyboard(webinar_id, lang),
        parse_mode='HTML'
    )

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