import logging

import telegram
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
    get_welcome_keyboard,
    get_hypno_webinar_keyboard,
    get_hypno_payment_keyboard,
    get_back_to_hypno_payment_keyboard
)
from bot.utils.logger import log_action

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

# ЗДЕСЬ УНИКАЛЬНАЯ ЛОГИКА ДЛЯ ВЕБА С ГИПНОЗОМ


async def show_hypno_webinar(update: Update, context: ContextTypes.DEFAULT_TYPE, is_back_action: bool = False):
    """Улучшенная версия с правильной обработкой возврата"""
    try:
        user_id = update.effective_user.id
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        # Для действия "Назад" используем специальный текст
        if is_back_action:
            webinar_text = "↩️ <b>Возврат к вебинару по гипнозу</b>\n\nВыберите часть для покупки:"
        else:
            webinar_text = "🎭 <b>Вебинар по эротическому гипнозу</b>\n\nВыберите часть для покупки:"

        reply_markup = get_hypno_webinar_keyboard(lang)

        try:
            await query.edit_message_text(
                text=webinar_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            log_action("hypno_webinar_shown", user_id, {"action": "back" if is_back_action else "open"})

        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                # Если сообщение не изменилось, просто игнорируем
                return
            raise

    except Exception as e:
        log_action("hypno_webinar_error", user_id, {"error": str(e)})
        try:
            await query.answer("⚠️ Ошибка при обновлении")
        except:
            pass


async def show_hypno_payment_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает методы оплаты для выбранной части"""
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        # Определяем выбранную часть
        part = query.data.replace("hypno_buy_", "")
        context.user_data['current_hypno_part'] = part

        await query.edit_message_text(
            text=f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']}</b>\n\nВыберите способ оплаты:",
            reply_markup=get_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in show_hypno_payment_methods: {e}")


async def back_to_webinars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к списку вебинаров"""
    await show_webinars_menu(update, context)

async def back_to_hypno_parts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат к выбору частей вебинара"""
    await show_hypno_webinar(update, context)


async def handle_hypno_part_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора части вебинара"""
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        # Парсим выбранную часть (1, 2 или both)
        part = query.data.split(":")[1]
        context.user_data['current_hypno_part'] = part

        await query.edit_message_text(
            text=f"💰 <b>Оплата {LANGUAGES[lang][f'part_{part}']}</b>\n\nВыберите способ оплаты:",
            reply_markup=get_hypno_payment_keyboard(lang, part),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in handle_hypno_part_selection: {e}")
        await query.answer("⚠️ Ошибка при выборе части")


async def handle_hypno_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора способа оплаты"""
    try:
        query = update.callback_query
        await query.answer()

        # Парсим данные: hypno_pay:валюта:часть
        _, currency, part = query.data.split(":")

        # Здесь добавьте логику обработки платежа
        await query.edit_message_text(
            text=f"ℹ️ Вы выбрали оплату {part} части в {currency}\n\nРеквизиты будут отправлены...",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in handle_hypno_payment: {e}")
        await query.answer("⚠️ Ошибка при выборе оплаты")



handlers = [
    CallbackQueryHandler(show_webinar_details, pattern="^webinar_details_"),

# ЗДЕСЬ УНИКАЛЬНЫЕ ОБРАБОТЧИКИ ДЛЯ ВЕБА С ГИПНОЗОМ
    CallbackQueryHandler(show_hypno_webinar, pattern="^webinar_hypno$"),
    CallbackQueryHandler(handle_hypno_part_selection, pattern="^hypno_part:"),
    CallbackQueryHandler(handle_hypno_payment, pattern="^hypno_pay:"),
    CallbackQueryHandler(back_to_webinars, pattern="^back_to_webinars$"),
    CallbackQueryHandler(back_to_hypno_parts, pattern="^back_to_hypno_parts$"),


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