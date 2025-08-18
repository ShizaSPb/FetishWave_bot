import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.database.notion_db import get_user_data
from bot.handlers.shared import update_menu_message
from bot.utils.languages import LANGUAGES
from bot.data.descriptions import DESCRIPTIONS
from bot.utils.keyboards import (
    get_upload_instructions_keyboard,
    get_donate_details_keyboard,
    get_back_to_donate_currency_keyboard, get_donate_currency_keyboard,
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
    get_audit_keyboard, get_buy_ads_thanks_keyboard, get_buy_ads_keyboard, get_offline_session_thanks_keyboard,
    get_session_menu_keyboard, get_offline_session_keyboard, get_online_session_keyboard,
    get_online_session_payment_keyboard, get_personal_account_keyboard
)
from bot.utils.logger import log_action
from config import ADMIN_CHAT_ID
from datetime import datetime

logger = logging.getLogger(__name__)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, cleanup_previous: bool = True):
    user_id = update.effective_user.id
    log_action("main_menu_render", user_id)

    try:
        query = update.callback_query
        if query:
            await query.answer()

        lang = context.user_data.get('lang', 'ru')
        is_registered = context.user_data.get('registered') or await check_registration(user_id)

        # Удаляем предыдущие сообщения при необходимости, но не трогаем то, которое будем редактировать
        if cleanup_previous:
            messages_to_delete = [
                'last_file_message_id',
                'last_confirmation_message_id',
                'last_menu_message_id',
            ]

            current_msg_id = None
            if update.callback_query and update.callback_query.message:
                current_msg_id = update.callback_query.message.message_id

            for msg_key in messages_to_delete:
                msg_id = context.user_data.get(msg_key)
                if not msg_id:
                    continue

                # Не удаляем сообщение, по кнопке которого пришёл этот callback — его мы собираемся редактировать
                if current_msg_id and msg_id == current_msg_id:
                    continue

                try:
                    await context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=msg_id
                    )
                except Exception as e:
                    log_action("message_deletion_failed", user_id, {
                        "message_type": msg_key,
                        "error": str(e)
                    })
                finally:
                    # В любом случае убираем флаг, чтобы не пытаться удалить повторно в будущем
                    context.user_data.pop(msg_key, None)

        # Отображаем главное меню
        if is_registered:
            await update_menu_message(
                update=update,
                context=context,
                text=LANGUAGES[lang]["main_menu"],
                reply_markup=get_main_menu_keyboard(lang),
                is_query=bool(query),
                menu_type='main'
            )
            log_action("main_menu_shown", user_id)
        else:
            await update_menu_message(
                update=update,
                context=context,
                text=LANGUAGES[lang]["registration_required"],
                reply_markup=get_welcome_keyboard(lang),
                is_query=bool(query),
                menu_type='main'
            )
            log_action("registration_required_shown", user_id)

    except Exception as e:
        log_action("menu_error", user_id, {"error": str(e)})
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

        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["products"],
            reply_markup=get_products_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='products'  # Добавлено
        )
        log_action("products_menu_shown", user_id)
    except Exception as e:
        log_action("products_menu_error", user_id, {"error": str(e)})
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

        await update_menu_message(
            update=update,
            context=context,
            text=DESCRIPTIONS[lang]["consultations"],
            reply_markup=get_consultations_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='consultations'  # Добавлено
        )
        log_action("consultations_menu_shown", user_id)
    except Exception as e:
        log_action("consultations_menu_error", user_id, {"error": str(e)})
        raise

async def show_mentoring_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("mentoring_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await update_menu_message(
            update=update,
            context=context,
            text=DESCRIPTIONS[lang]["mentoring"],
            reply_markup=get_mentoring_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='mentoring'  # Добавлено
        )
        log_action("mentoring_menu_shown", user_id)
    except Exception as e:
        log_action("mentoring_menu_error", user_id, {"error": str(e)})
        raise

async def show_page_audit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("page_audit_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await update_menu_message(
            update=update,
            context=context,
            text=DESCRIPTIONS[lang]["page_audit"],
            reply_markup=get_page_audit_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='page_audit'  # Добавлено
        )
        log_action("page_audit_menu_shown", user_id)
    except Exception as e:
        log_action("page_audit_menu_error", user_id, {"error": str(e)})
        raise

async def show_private_channel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("private_channel_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await update_menu_message(
            update=update,
            context=context,
            text=DESCRIPTIONS[lang]["private_channel"],
            reply_markup=get_private_channel_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='private_channel'  # Добавлено
        )
        log_action("private_channel_menu_shown", user_id)
    except Exception as e:
        log_action("private_channel_menu_error", user_id, {"error": str(e)})
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

        message_text = (
            "🔍 <b>{}</b>\n\n{}\n\n{}".format(
                LANGUAGES[lang]["audit_personal"],
                LANGUAGES[lang]["audit_personal_desc"],
                "После заполнения формы мы свяжемся с вами для уточнения деталей." if lang == "ru" else
                "After submitting the form, we'll contact you to discuss details."
            )
        )

        await query.edit_message_text(
            text=message_text,
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
        audit_type = query.data.split('_')[-1]  # Получаем тип аудита (personal/company)

        # Отправка уведомления админу
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        audit_type_localized = LANGUAGES[lang][f"audit_{audit_type}"]

        admin_message = (
            f"🚀 <b>Новая заявка на аудит</b>\n\n"
            f"🔹 Тип: {audit_type_localized}\n"
            f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Время: {datetime.now().strftime(DESCRIPTIONS[lang]['time_format'])}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        # Подтверждение пользователю
        await query.edit_message_text(
            text=LANGUAGES[lang]["audit_thanks"],
            reply_markup=get_audit_thanks_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("audit_notification_sent", user.id, {"audit_type": audit_type})
    except Exception as e:
        log_action("audit_notification_failed", user.id, {
            "error": str(e),
            "audit_type": audit_type
        })
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Audit notification error: {e}", exc_info=True)

async def show_buy_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("buy_ads_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        message_text = (
            f"{LANGUAGES[lang]['buy_ads_title']}\n\n"
            f"{LANGUAGES[lang]['buy_ads_desc']}\n\n"
            "После заполнения формы мы свяжемся с вами для уточнения деталей."
            if lang == "ru" else
            f"{LANGUAGES[lang]['buy_ads_title']}\n\n"
            f"{LANGUAGES[lang]['buy_ads_desc']}\n\n"
            "After submitting the form, we'll contact you to discuss details."
        )

        await query.edit_message_text(
            text=message_text,
            reply_markup=get_buy_ads_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("buy_ads_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_buy_ads: {e}")

async def handle_buy_ads_filled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        lang = context.user_data.get('lang', 'ru')

        # Отправка уведомления админу
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        admin_message = (
            f"🚀 <b>Новая заявка на покупку рекламы</b>\n\n"
            f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        # Подтверждение пользователю
        await query.edit_message_text(
            text=LANGUAGES[lang]["buy_ads_thanks"],
            reply_markup=get_buy_ads_thanks_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("buy_ads_notification_sent", user.id)
    except Exception as e:
        log_action("buy_ads_notification_failed", user.id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Buy ads notification error: {e}")

async def show_session_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("session_menu_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["book_session"],
            reply_markup=get_session_menu_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='session'  # Добавлено
        )
        log_action("session_menu_shown", user_id)
    except Exception as e:
        log_action("session_menu_error", user_id, {"error": str(e)})
        raise

async def show_offline_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("offline_session_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["offline_session_desc"],
            reply_markup=get_offline_session_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("offline_session_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_offline_session: {e}")

async def handle_offline_session_filled(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        lang = context.user_data.get('lang', 'ru')

        # Отправка уведомления админу
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        admin_message = (
            f"🚀 <b>Новая заявка на оффлайн сессию</b>\n\n"
            f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            parse_mode='HTML'
        )

        # Подтверждение пользователю
        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["offline_session_thanks"],
            reply_markup=get_offline_session_thanks_keyboard(lang),
            parse_mode='HTML'
        )

        log_action("offline_session_notification_sent", user.id)
    except Exception as e:
        log_action("offline_session_notification_failed", user.id, {"error": str(e)})
        await query.answer("⚠️ Ошибка при отправке уведомления")
        logger.error(f"Offline session notification error: {e}")

async def show_online_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("online_session_open", user_id)

    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        await query.edit_message_text(
            text=DESCRIPTIONS[lang]["online_session_desc"],
            reply_markup=get_online_session_keyboard(lang),
            parse_mode='HTML'
        )
    except Exception as e:
        log_action("online_session_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_online_session: {e}")


async def show_online_session_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("online_payment_options_open", user_id)

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
        log_action("online_payment_options_error", user_id, {"error": str(e)})
        logger.error(f"Error in show_online_session_payment_options: {e}")


async def show_personal_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    try:
        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["personal_account"],
            reply_markup=get_personal_account_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='personal_account'
        )
    except Exception as e:
        log_action("personal_account_error", user_id, {"error": str(e)})
        raise



async def show_donate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Экран доната с выбором валюты"""
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')
    try:
        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["donate"],
            reply_markup=get_donate_currency_keyboard(lang),
            is_query=True,
            parse_mode='HTML',
            menu_type='donate_menu'
        )
        log_action("donate_menu_shown", user_id)
    except Exception as e:
        log_action("donate_menu_error", user_id, {"error": str(e)})
        raise




async def handle_donate_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора валюты для доната"""
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')

    data = query.data
    if data == "donate_rub":
        details = DESCRIPTIONS[lang]["payment_rub_details"]
        ckey = "rub"
    elif data == "donate_crypto":
        details = DESCRIPTIONS[lang]["payment_crypto_details"]
        ckey = "crypto"
    elif data == "donate_eur":
        details = DESCRIPTIONS[lang]["payment_eur_details"]
        ckey = "eur"
    else:
        return

    await query.edit_message_text(
        text=details,
        reply_markup=get_donate_details_keyboard(lang, ckey),
        parse_mode='HTML'
    )
    log_action("donate_currency_shown", user_id, {"currency": ckey})



async def handle_donate_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Включает режим ожидания скриншота для доната.
    Колбэк: donate_upload_screenshot:<rub|crypto|eur>
    """
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get('lang', 'ru')
    try:
        currency_key = query.data.split(":")[1]

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = f"donate_{currency_key}"
        context.user_data['last_back_pattern'] = "menu_donate"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, "menu_donate"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id
    except Exception as e:
        await query.answer("⚠️ Ошибка, попробуйте ещё раз", show_alert=True)
handlers = [
# Main menus
    #CallbackQueryHandler(show_main_menu, pattern="^main_menu$"),
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
    CallbackQueryHandler(show_buy_ads, pattern="^menu_buy_ads$"),
    CallbackQueryHandler(handle_buy_ads_filled, pattern="^buy_ads_filled$"),
    CallbackQueryHandler(show_session_menu, pattern="^menu_book_session$"),
    CallbackQueryHandler(show_offline_session, pattern="^offline_session$"),
    CallbackQueryHandler(show_online_session, pattern="^online_session$"),
    # CallbackQueryHandler(show_online_session_payment_options, pattern="^online_session_payment$"),
    CallbackQueryHandler(handle_offline_session_filled, pattern="^offline_session_filled$"),
    CallbackQueryHandler(show_donate_menu, pattern="^menu_donate$"),
    CallbackQueryHandler(handle_donate_currency, pattern="^donate_(rub|crypto|eur)$"),
    CallbackQueryHandler(handle_donate_upload_screenshot, pattern="^donate_upload_screenshot:(rub|crypto|eur)$"),
]