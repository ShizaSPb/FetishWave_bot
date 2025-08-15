import logging
from datetime import datetime
import os
from pathlib import Path
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
    get_online_session_payment_keyboard, get_back_to_currency_selection_keyboard,
    get_upload_instructions_keyboard, get_success_upload_keyboard, get_invalid_file_keyboard,
)
from bot.utils.logger import log_action
from config import ADMIN_CHAT_ID
from bot.utils.admin_keyboards import get_admin_payment_actions_kb
from bot.handlers.admin_payments import remember_pending_payment
try:
    from bot.database.notion_payments import create_payment_record  # опционально
except Exception:
    create_payment_record = None

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.heic', '.heif'}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'application/pdf',
    'image/heic',
    'image/heif'
}


def is_file_allowed(file_name: str, mime_type: str = None) -> bool:
    """Проверяет файл по расширению и MIME-типу с конвертацией HEIC"""
    file_ext = Path(file_name).suffix.lower()

    # Разрешаем HEIC/HEIF только от iPhone
    if file_ext in {'.heic', '.heif'}:
        return True

    # Стандартная проверка для других форматов
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        return False

    return file_ext in ALLOWED_EXTENSIONS

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
            reply_markup=get_back_to_currency_selection_keyboard(lang),
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


async def handle_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        webinar_id = query.data.split(":")[1]

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = f"webinar_{webinar_id}"
        # Сохраняем шаблон для кнопки "Назад"
        context.user_data['last_back_pattern'] = f"payment_methods_{webinar_id}"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, f"payment_methods_{webinar_id}"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id

    except Exception as e:
        logger.error(f"Error in handle_upload_screenshot: {e}")


async def handle_hypno_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.split(":")[1]

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = f"hypno_part_{part}"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, f"hypno_back_to_payment_{part}"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id
    except Exception as e:
        logger.error(f"Error in handle_hypno_upload_screenshot: {e}")


async def handle_femdom_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        part = query.data.split(":")[1]

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = f"femdom_part_{part}"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, f"femdom_back_to_payment_{part}"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id
    except Exception as e:
        logger.error(f"Error in handle_femdom_upload_screenshot: {e}")


async def handle_consultation_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')
        consultation_type = query.data.split(":")[1]

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = f"consultation_{consultation_type}"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, f"consultation_back:{consultation_type}"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id
    except Exception as e:
        logger.error(f"Error in handle_consultation_upload_screenshot: {e}")


async def handle_online_session_upload_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        lang = context.user_data.get('lang', 'ru')

        context.user_data['awaiting_screenshot'] = True
        context.user_data['current_payment_type'] = "online_session"

        message = await query.edit_message_text(
            text=LANGUAGES[lang]["upload_payment_instructions"],
            reply_markup=get_upload_instructions_keyboard(lang, "online_session_payment"),
            parse_mode='HTML'
        )
        context.user_data['last_instructions_message_id'] = message.message_id
    except Exception as e:
        logger.error(f"Error in handle_online_session_upload_screenshot: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'ru')

    if not context.user_data.get('awaiting_screenshot'):
        return

    # Проверяем тип файла и получаем file_id
    file_id = None
    is_document = False
    is_valid = False
    file_name = ""

    if update.message.document:
        file = update.message.document
        file_name = file.file_name or ""
        if (file.mime_type in ALLOWED_MIME_TYPES and
                is_file_allowed(file_name, file.mime_type)):
            file_id = file.file_id
            is_document = True
            is_valid = True
    elif update.message.photo:
        file = update.message.photo[-1]  # Берем самое большое фото
        file_id = file.file_id
        file_name = f"photo_{file.file_id}.jpg"
        is_valid = is_file_allowed(file_name)
    else:
        is_valid = False

    if not is_valid:
        try:
            # Удаляем неверный файл
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )

            # Формируем детальное сообщение об ошибке
            error_message = (
                f"⚠️ {LANGUAGES[lang]['invalid_file_type']}\n\n"
                f"Допустимые форматы:\n"
                f"- JPG/JPEG (.jpg, .jpeg)\n"
                f"- PNG (.png)\n"
                f"- PDF (.pdf)\n\n"
                f"HEIC и другие форматы не поддерживаются!"
            )

            # Отправляем сообщение с кнопкой назад
            back_pattern = context.user_data.get('last_back_pattern', 'main_menu')
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                reply_markup=get_invalid_file_keyboard(lang, back_pattern),
                parse_mode='HTML'
            )
            return
        except Exception as e:
            logger.error(f"Failed to handle invalid file: {e}")
            return

    try:
        payment_type = context.user_data.get('current_payment_type', 'unknown')
        user = update.effective_user

        # Удаляем предыдущее сообщение с инструкциями
        if 'last_instructions_message_id' in context.user_data:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['last_instructions_message_id']
                )
            except Exception as e:
                logger.error(f"Failed to delete instructions message: {e}")

        # Формируем текст уведомления для админа
        user_info = f"@{user.username}" if user.username else f"ID: {user.id}"
        payment_type_localized = {
            'webinar_hypno': "Вебинар по гипнозу",
            'webinar_femdom': "Вебинар по фемдом",
            'consultation_love': "Консультация (личная жизнь)",
            'consultation_work': "Консультация (работа)",
            'online_session': "Онлайн сессия",
            'donate_rub': "Донат (RUB)",
            'donate_crypto': "Донат (Crypto USDT TRC20)",
            'donate_eur': "Донат (EUR)"
        }.get(payment_type, payment_type)

        admin_message = (
            f"📸 <b>Новый скриншот оплаты</b>\n\n"
            f"🔹 Тип: {payment_type_localized}\n"
            f"👤 Пользователь: <a href='tg://user?id={user.id}'>{user_info}</a>\n"
            f"🆔 ID: {user.id}\n"
            f"📅 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        # Отправляем уведомление админу
        # Сохраняем «платёж» для кнопок + создаём черновик в Notion (если настроено)
        notion_payment_id = None
        if create_payment_record:
            try:
                notion_payment_id = await create_payment_record(
                    user_telegram_id=user.id,
                    payment_type=str(payment_type),
                    proof_file_id=file_id,
                    product_code=None,  # при желании укажите код продукта
                    username=user.username,
                    name=user.full_name,
                )
            except Exception as e:
                logger.warning("Failed to create payment in Notion: %s", e)

        payment_id = remember_pending_payment(
            context,
            user_id=user.id,
            payment_type=str(payment_type),
            product_code=None,  # при желании укажите код продукта
            notion_payment_id=notion_payment_id,
        )
        kb = get_admin_payment_actions_kb(payment_id)

        try:
            if is_document:
                await context.bot.send_document(
                    chat_id=ADMIN_CHAT_ID,
                    document=file_id,
                    caption=admin_message,
                    parse_mode='HTML',
                    reply_markup=kb,
                )
            else:
                await context.bot.send_photo(
                    chat_id=ADMIN_CHAT_ID,
                    photo=file_id,
                    caption=admin_message,
                    parse_mode='HTML',
                    reply_markup=kb,
                )
        except Exception as e:
            logger.error(f"Failed to send file to admin: {e}")
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"{admin_message}\n\n⚠️ Не удалось отправить файл (ID: {file_id})",
                parse_mode='HTML',
                reply_markup=kb,
            )

        # Сохраняем ID сообщения с файлом
        context.user_data['last_file_message_id'] = update.message.message_id

        # Удаляем флаги ожидания
        del context.user_data['awaiting_screenshot']
        del context.user_data['current_payment_type']
        if 'last_instructions_message_id' in context.user_data:
            del context.user_data['last_instructions_message_id']

        # Отправляем подтверждение пользователю
        confirmation_key = "donation_screenshot_received" if str(payment_type).startswith("donate_") else "screenshot_received"
        confirmation_msg = await update.message.reply_text(
            LANGUAGES[lang][confirmation_key],
            reply_markup=get_success_upload_keyboard(lang)
        )

        # Сохраняем ID подтверждения для возможного удаления
        context.user_data['last_confirmation_message_id'] = confirmation_msg.message_id

        log_action("payment_screenshot_uploaded", user_id, {
            "payment_type": payment_type,
            "file_id": file_id,
            "file_name": file_name,
            "file_type": "document" if is_document else "photo",
            "admin_notified": True
        })

    except Exception as e:
        logger.error(f"Error processing payment screenshot: {e}")
        await update.message.reply_text(
            LANGUAGES[lang]["upload_error"],
            reply_markup=get_invalid_file_keyboard(lang, 'main_menu')
        )


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

    # Новые обработчики для загрузки скриншотов
    CallbackQueryHandler(handle_upload_screenshot, pattern="^upload_screenshot:"),
    CallbackQueryHandler(handle_hypno_upload_screenshot, pattern="^hypno_upload_screenshot:"),
    CallbackQueryHandler(handle_femdom_upload_screenshot, pattern="^femdom_upload_screenshot:"),
    CallbackQueryHandler(handle_consultation_upload_screenshot, pattern="^consultation_upload_screenshot:"),
    CallbackQueryHandler(handle_online_session_upload_screenshot, pattern="^online_session_upload_screenshot$"),
]