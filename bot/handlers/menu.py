import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data
from bot.utils.languages import LANGUAGES
from bot.data.descriptions import DESCRIPTIONS
from bot.utils.keyboards import (
    get_main_menu_keyboard,
    get_products_menu_keyboard,
    get_consultations_menu_keyboard,
    get_mentoring_menu_keyboard,
    get_page_audit_menu_keyboard,
    get_private_channel_menu_keyboard,
    get_welcome_keyboard,
    get_cooperation_keyboard,
    get_back_to_menu_keyboard,
    get_personal_consultation_keyboard,
    get_company_consultation_keyboard,
    get_consultation_payment_keyboard, get_mentoring_keyboard, get_mentoring_thanks_keyboard, get_audit_thanks_keyboard,
    get_audit_keyboard
)
from bot.utils.logger import log_action
from config import ADMIN_CHAT_ID
from datetime import datetime

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(context, 'last_processed_message'):
        del context.last_processed_message
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

async def show_offer_cooperation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("offer_cooperation_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["offer_cooperation"],
            reply_markup=get_cooperation_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("offer_cooperation_menu_shown", user_id)
    except Exception as e:
        log_action("offer_cooperation_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_offer_cooperation_menu: {e}", exc_info=True)
        raise

async def show_consultations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("consultations_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["consultations"],
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
            text=DESCRIPTIONS[lang]["mentoring"],
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
            text=DESCRIPTIONS[lang]["page_audit"],
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
            text=DESCRIPTIONS[lang]["private_channel"],
            reply_markup=get_private_channel_menu_keyboard(lang),
            parse_mode='HTML'
        )
        log_action("private_channel_menu_shown", user_id)
    except Exception as e:
        log_action("private_channel_menu_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_private_channel_menu: {e}", exc_info=True)
        raise

async def handle_cooperation_filled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        lang = context.user_data.get('lang', 'ru')

        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        admin_message = (
            f"🚀 <b>Новая заявка на сотрудничество</b>\n\n"
            f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["cooperation_thanks"],
            reply_markup=get_back_to_menu_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("cooperation_notification_sent", user.id)
    except Exception as e:
        log_action("cooperation_notification_failed", user.id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Cooperation notification error: {e}")

async def show_personal_consultation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("personal_consultation_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["consultation_personal_desc"],
            reply_markup=get_personal_consultation_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("personal_consultation_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_personal_consultation_menu: {e}")

async def handle_consultation_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("consultation_type_selected", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        consultation_type = query.data.split(":")[1]
        context.user_data['current_consultation'] = consultation_type

        description = DESCRIPTIONS[lang].get(
            f"consultation_{consultation_type}_desc",
            LANGUAGES[lang].get("default_description", "")
        )

        await query.edit_message_text(
            text=f"{description}\n\n{LANGUAGES[lang]['choose_payment']}",
            reply_markup=get_consultation_payment_keyboard(lang, consultation_type),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("consultation_type_error", user_id, {"error": str(e)})
        logger.error(f"Error in handle_consultation_type_selection: {e}")

async def show_company_consultation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("company_consultation_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["consultation_company_desc"],
            reply_markup=get_company_consultation_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("company_consultation_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_company_consultation_menu: {e}")

async def back_to_consultation_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        consultation_type = query.data.split(":")[1]

        if consultation_type in ["love", "work"]:
            await show_personal_consultation_menu(update, context)
        else:
            await show_company_consultation_menu(update, context)
    except Exception as e:
        logger.error(f"Error in back_to_consultation_type: {e}")


async def show_personal_mentoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("personal_mentoring_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang].get("mentoring_personal_desc", "Менторинг для личных целей"),
            reply_markup=get_mentoring_keyboard(lang, "personal"),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("personal_mentoring_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_personal_mentoring: {e}")

async def show_company_mentoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("company_mentoring_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang].get("mentoring_company_desc", "Менторинг для компаний"),
            reply_markup=get_mentoring_keyboard(lang, "company"),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("company_mentoring_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_company_mentoring: {e}")


async def handle_mentoring_filled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        lang = context.user_data.get('lang', 'ru')

        # Отправка уведомления админу (прежний код)
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        admin_message = f"🚀 <b>Новая заявка на менторинг</b>\n\n👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n🆔 ID: {user.id}\n📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        # Подтверждение пользователю с возвратом к меню менторинга
        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["mentoring_thanks"],
            reply_markup=get_mentoring_thanks_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("mentoring_notification_sent", user.id)
    except Exception as e:
        log_action("mentoring_notification_failed", user.id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Mentoring notification error: {e}")


async def back_to_mentoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        mentoring_type = context.user_data.get('last_mentoring_type', 'personal')

        if mentoring_type == 'personal':
            await show_personal_mentoring(update, context)
        else:
            await show_company_mentoring(update, context)
    except Exception as e:
        logger.error(f"Error in back_to_mentoring: {e}")
        await query.answer("⚠️ Ошибка при возврате")

async def show_personal_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("personal_audit_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang].get("audit_personal_desc", "Аудит страниц для личных целей"),
            reply_markup=get_audit_keyboard(lang, "personal"),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("personal_audit_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_personal_audit: {e}")

async def show_company_audit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("company_audit_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang].get("audit_company_desc", "Аудит страниц для компаний"),
            reply_markup=get_audit_keyboard(lang, "company"),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("company_audit_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_company_audit: {e}")

async def handle_audit_filled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        lang = context.user_data.get('lang', 'ru')

        # Отправка уведомления админу
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        admin_message = f"🚀 <b>Новая заявка на аудит страниц</b>\n\n👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n🆔 ID: {user.id}\n📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        # Подтверждение пользователю
        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["audit_thanks"],
            reply_markup=get_audit_thanks_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("audit_notification_sent", user.id)
    except Exception as e:
        log_action("audit_notification_failed", user.id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Audit notification error: {e}")

handlers = [
    # Main menus
    CallbackQueryHandler(show_main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(show_products_menu, pattern="^menu_products$"),
    CallbackQueryHandler(show_offer_cooperation_menu, pattern="^menu_offer_cooperation$"),
    CallbackQueryHandler(handle_cooperation_filled, pattern="^cooperation_filled$"),
    CallbackQueryHandler(show_consultations_menu, pattern="^menu_consultations$"),
    CallbackQueryHandler(show_mentoring_menu, pattern="^menu_mentoring$"),
    CallbackQueryHandler(show_page_audit_menu, pattern="^menu_page_audit$"),
    CallbackQueryHandler(show_private_channel_menu, pattern="^menu_private_channel$"),
    CallbackQueryHandler(show_personal_consultation_menu, pattern="^consultation_personal$"),
    CallbackQueryHandler(show_company_consultation_menu, pattern="^consultation_company$"),
    CallbackQueryHandler(handle_consultation_type_selection, pattern="^consultation_type:"),
    CallbackQueryHandler(back_to_consultation_type, pattern="^consultation_back:"),
    CallbackQueryHandler(show_personal_mentoring, pattern="^mentoring_personal$"),
    CallbackQueryHandler(show_company_mentoring, pattern="^mentoring_company$"),
    CallbackQueryHandler(handle_mentoring_filled, pattern="^mentoring_filled_"),
    CallbackQueryHandler(show_personal_audit, pattern="^audit_personal$"),
    CallbackQueryHandler(show_company_audit, pattern="^audit_company$"),
    CallbackQueryHandler(handle_audit_filled, pattern="^audit_filled_"),
]