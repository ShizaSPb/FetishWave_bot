import logging
import html
from email_validator import validate_email, EmailNotValidError
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bot.handlers.menu import show_main_menu, show_personal_account
from bot.utils.keyboards import get_welcome_keyboard, get_main_menu_keyboard, get_edit_profile_menu_keyboard
from bot.utils.languages import LANGUAGES
from bot.services.actions import log_action
from bot.handlers import update_menu_message
from bot.database.notion_db import update_user_in_notion, get_user_data, notion
from config import NOTION_USERS_DB_ID

logger = logging.getLogger(__name__)

# --- Состояния для раздела «Изменить личные данные»
EDIT_NAME_STATE = 100
EDIT_EMAIL_STATE = 101


# ---------- ВСПОМОГАТЕЛЬНОЕ ----------
async def _safe_del(context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_id: int | None):
    """Безопасно удалить сообщение по id (игнорировать любые ошибки)."""
    if not msg_id:
        return
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except Exception:
        pass

def _build_edit_profile_text(lang: str, name: str | None, email: str | None) -> str:
    name_escaped  = html.escape(str(name  or LANGUAGES[lang]["not_specified"]),  quote=False)
    email_escaped = html.escape(str(email or LANGUAGES[lang]["not_specified"]), quote=False)
    return (
        f"<b>{LANGUAGES[lang]['your_name']}:</b> {name_escaped}\n"
        f"<b>{LANGUAGES[lang]['your_email']}:</b> {email_escaped}\n"
        f"{html.escape(LANGUAGES[lang]['edit_profile_title'], quote=False)}"
    )

async def _refresh_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str):
    # ---------- Обновить текст уже показанного меню «Изменить личные данные» без дублирования.----------
    user = await get_user_data(update.effective_user.id)
    text = _build_edit_profile_text(lang, (user or {}).get("name"), (user or {}).get("email"))
    menu_msg_id = context.user_data.get("edit_menu_msg_id")
    if not menu_msg_id:
        return
    try:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=menu_msg_id,
            text=text,
            reply_markup=get_edit_profile_menu_keyboard(lang),
            parse_mode="HTML",
        )
    except Exception:
        # если вдруг сообщение исчезло/не редактируется — молча игнорируем (не шлём новое, чтобы не плодить дубликаты)
        pass


# ---------- МЕНЮ «ИЗМЕНИТЬ ЛИЧНЫЕ ДАННЫЕ» ----------
async def show_edit_profile_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "ru")
    if update.callback_query:
        await update.callback_query.answer()

    # текущие данные пользователя
    try:
        user = await get_user_data(update.effective_user.id)
    except Exception:
        user = None

    text = _build_edit_profile_text(lang, (user or {}).get("name"), (user or {}).get("email"))

    await update_menu_message(
        update=update,
        context=context,
        text=text,
        reply_markup=get_edit_profile_menu_keyboard(lang),
        is_query=bool(update.callback_query),
        parse_mode="HTML",
        menu_type="edit_profile_menu",
    )

    # сохраним id сообщения меню, чтобы потом редактировать его «на месте»
    if update.effective_message:
        context.user_data["edit_menu_msg_id"] = update.effective_message.message_id





# ---------- СМЕНА ИМЕНИ ----------
async def start_edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Попросить ввести имя отдельным сообщением (чтобы потом можно было удалить оба сообщения)."""
    lang = context.user_data.get("lang", "ru")
    q = update.callback_query
    if q:
        await q.answer()

    prompt = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=LANGUAGES[lang]["enter_name"],
        parse_mode="HTML",
    )
    context.user_data["prompt_name_msg_id"] = prompt.message_id
    return EDIT_NAME_STATE


async def handle_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принять имя, провалидировать, обновить в Notion, очистить сообщения и вернуть меню."""
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id

    # Проверим, что пришёл текст
    if not (update.message and update.message.text):
        await update.message.reply_text(LANGUAGES[lang]["enter_name_again"])
        return EDIT_NAME_STATE

    name = update.message.text.strip()

    # Валидация (как в регистрации)
    import re as _re
    if len(name) < 2:
        await update.message.reply_text(f"{LANGUAGES[lang]['name_too_short']}\n{LANGUAGES[lang]['enter_name_again']}")
        return EDIT_NAME_STATE
    if len(name) > 30:
        await update.message.reply_text(f"{LANGUAGES[lang]['name_too_long']}\n{LANGUAGES[lang]['enter_name_again']}")
        return EDIT_NAME_STATE
    if _re.search(r'[0-9_!@#$%^&*(),.?":{}|<>]', name):
        await update.message.reply_text(f"{LANGUAGES[lang]['name_invalid_chars']}\n{LANGUAGES[lang]['enter_name_again']}")
        return EDIT_NAME_STATE
    if _re.search(r"(http|www|\.com|\.ru|\.net)", name, _re.I):
        await update.message.reply_text(f"{LANGUAGES[lang]['name_suspicious']}\n{LANGUAGES[lang]['enter_name_again']}")
        return EDIT_NAME_STATE
    if name.lower() in ["admin", "support", "test", "user"]:
        await update.message.reply_text(f"{LANGUAGES[lang]['name_generic']}\n{LANGUAGES[lang]['enter_name_again']}")
        return EDIT_NAME_STATE

    # Найдём страницу в Notion по Telegram ID
    try:
        resp = notion.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": user_id}},
        )
        if not resp.get("results"):
            await update.message.reply_text(LANGUAGES[lang]["registration_required"])
            return ConversationHandler.END
        page_id = resp["results"][0]["id"]
    except Exception:
        await update.message.reply_text(LANGUAGES[lang]["registration_failed"])
        return ConversationHandler.END

    # Текущий email (из карточки пользователя) — чтобы отдать оба поля в update_user_in_notion
    user = await get_user_data(user_id)
    current_email = (user or {}).get("email") or ""

    # Если раньше ввели email (цепочка "сначала email → потом имя")
    pending_email = context.user_data.pop("pending_email", None)
    if pending_email:
        current_email = pending_email

    if not current_email:
        # Email ещё не известен — попросим e-mail и запомним имя
        context.user_data["pending_name"] = name
        await update.message.reply_text(LANGUAGES[lang]["enter_email"])
        return EDIT_EMAIL_STATE

    # Обновляем оба поля (Notion update ожидает name+email)
    ok = await update_user_in_notion(
        page_id,
        {"telegram_id": user_id, "name": name, "email": current_email},
    )

    if ok:
        success = await update.message.reply_text(LANGUAGES[lang]["profile_update_success"])

        # Удаляем 3 сообщения: приглашение, ответ пользователя, успешное
        await _safe_del(context, update.effective_chat.id, context.user_data.pop("prompt_name_msg_id", None))
        await _safe_del(context, update.effective_chat.id, update.message.message_id)
        await _safe_del(context, update.effective_chat.id, success.message_id)
        await _refresh_edit_menu(update, context, lang)

        # НИЧЕГО не отправляем заново — меню уже на экране
    else:
        await update.message.reply_text(LANGUAGES[lang]["profile_update_failed"])

    return ConversationHandler.END


# ---------- СМЕНА EMAIL ----------
async def start_edit_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Попросить ввести email отдельным сообщением и запомнить message_id для последующего удаления."""
    lang = context.user_data.get("lang", "ru")
    q = update.callback_query
    if q:
        await q.answer()

    prompt = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=LANGUAGES[lang]["enter_email"],
        parse_mode="HTML",
    )
    context.user_data["prompt_email_msg_id"] = prompt.message_id
    return EDIT_EMAIL_STATE


async def handle_new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принять email, провалидировать, обновить (возможен догон имени), очистить сообщения и вернуть меню."""
    lang = context.user_data.get("lang", "ru")
    user_id = update.effective_user.id

    # Проверим, что пришёл текст
    if not (update.message and update.message.text):
        await update.message.reply_text(LANGUAGES[lang]["enter_email_again"])
        return EDIT_EMAIL_STATE

    email_raw = update.message.text.strip()

    # Валидация email (как в регистрации)
    try:
        valid = validate_email(
            email_raw,
            check_deliverability=True,
            allow_smtputf8=False,
            allow_empty_local=False,
        )
        email_norm = valid.normalized
    except EmailNotValidError as e:
        msg = str(e)
        if "The domain name" in msg and "does not exist" in msg:
            await update.message.reply_text(
                f"{LANGUAGES[lang]['email_domain_error']}\n{LANGUAGES[lang]['enter_email_again']}"
            )
        elif "There must be something after" in msg:
            await update.message.reply_text(
                f"{LANGUAGES[lang]['email_incomplete']}\n{LANGUAGES[lang]['enter_email_again']}"
            )
        else:
            await update.message.reply_text(
                f"{LANGUAGES[lang]['invalid_email']}\n{LANGUAGES[lang]['enter_email_again']}"
            )
        return EDIT_EMAIL_STATE

    # Найдём страницу в Notion по Telegram ID
    try:
        resp = notion.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": user_id}},
        )
        if not resp.get("results"):
            await update.message.reply_text(LANGUAGES[lang]["registration_required"])
            return ConversationHandler.END
        page_id = resp["results"][0]["id"]
    except Exception:
        await update.message.reply_text(LANGUAGES[lang]["registration_failed"])
        return ConversationHandler.END

    # Если ранее ввели имя (pending_name) — обновляем оба
    pending_name = context.user_data.pop("pending_name", None)
    if pending_name:
        ok = await update_user_in_notion(
            page_id,
            {"telegram_id": user_id, "name": pending_name, "email": email_norm},
        )
        if ok:
            success = await update.message.reply_text(LANGUAGES[lang]["profile_update_success"])
            # Удаляем 3 сообщения: приглашение, ответ пользователя, успешное
            await _safe_del(context, update.effective_chat.id, context.user_data.pop("prompt_email_msg_id", None))
            await _safe_del(context, update.effective_chat.id, update.message.message_id)
            await _safe_del(context, update.effective_chat.id, success.message_id)
            await _refresh_edit_menu(update, context, lang)

            await update_menu_message(
                update=update,
                context=context,
                text=LANGUAGES[lang]["edit_profile_title"],
                reply_markup=get_edit_profile_menu_keyboard(lang),
                is_query=False,
                parse_mode="HTML",
                menu_type="edit_profile_menu",
            )
        else:
            await update.message.reply_text(LANGUAGES[lang]["profile_update_failed"])
        return ConversationHandler.END

    # Иначе — возьмём текущее имя из Notion; если пусто, попросим имя и сохраним pending_email
    user = await get_user_data(user_id)
    current_name = (user or {}).get("name") or ""
    if not current_name:
        context.user_data["pending_email"] = email_norm
        await update.message.reply_text(LANGUAGES[lang]["enter_name"])
        return EDIT_NAME_STATE

    # Обновляем (name уже есть в Notion)
    ok = await update_user_in_notion(
        page_id, {"telegram_id": user_id, "name": current_name, "email": email_norm}
    )
    if ok:
        success = await update.message.reply_text(LANGUAGES[lang]["profile_update_success"])

        # Удаляем 3 сообщения: приглашение, ответ пользователя, успешное
        await _safe_del(context, update.effective_chat.id, context.user_data.pop("prompt_email_msg_id", None))
        await _safe_del(context, update.effective_chat.id, update.message.message_id)
        await _safe_del(context, update.effective_chat.id, success.message_id)

        # Меню НЕ пересылаем — старое уже есть
    else:
        await update.message.reply_text(LANGUAGES[lang]["profile_update_failed"])

    return ConversationHandler.END


# ---------- ПРОЧИЕ ТВОИ ОБРАБОТЧИКИ ----------
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
        context.user_data["registered"] = True
        await show_main_menu(update, context)
    else:
        log_action("user_not_authenticated", user_id)
        await query.edit_message_text(text=LANGUAGES[lang]["welcome"], reply_markup=get_welcome_keyboard(lang))


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    log_action("main_menu_request", user_id)

    try:
        query = update.callback_query
        await query.answer()

        # Убедимся, что язык установлен
        if "lang" not in context.user_data:
            context.user_data["lang"] = "ru"

        await show_main_menu(update, context)
        log_action("main_menu_shown", user_id)
    except Exception as e:
        log_action("main_menu_error", user_id, {"error": str(e)})
        # Пытаемся показать меню заново
        lang = context.user_data.get("lang", "ru")
        await update_menu_message(
            update=update,
            context=context,
            text=LANGUAGES[lang]["main_menu"],
            reply_markup=get_main_menu_keyboard(lang),
            is_query=True,
            menu_type="main",
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
    current_lang = context.user_data.get("lang", "ru")
    new_lang = "en" if current_lang == "ru" else "ru"
    context.user_data["lang"] = new_lang

    # Сначала обновляем интерфейс
    await show_personal_account(update, context)
    log_action("language_changed_ui", user_id, {"new_language": new_lang})

    # Затем запускаем фоновую задачу для Notion
    context.application.create_task(_update_language_in_notion(user_id, new_lang))


async def _update_language_in_notion(user_id: int, new_lang: str):
    """Фоновая задача для обновления языка в Notion."""
    try:
        response = notion.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": user_id}},
        )

        if response["results"]:
            page_id = response["results"][0]["id"]
            notion.pages.update(page_id=page_id, properties={"Language": {"select": {"name": new_lang}}})
            log_action("notion_language_updated", user_id, {"new_language": new_lang})
    except Exception as e:
        logger.error("Background Notion update failed: %s", e, exc_info=True)
        log_action("notion_language_update_failed", user_id, {"error": str(e)})


# ---------- РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ----------
handlers = [
    CallbackQueryHandler(language_selection, pattern="^set_lang_"),
    CallbackQueryHandler(main_menu, pattern="^main_menu$"),
    CallbackQueryHandler(handle_personal_account, pattern="^menu_personal_account$"),
    CallbackQueryHandler(handle_change_language, pattern="^personal_change_lang$"),

    # Меню «Изменить личные данные» и его ветки
    CallbackQueryHandler(show_edit_profile_menu, pattern="^personal_edit$"),
    ConversationHandler(
        entry_points=[CallbackQueryHandler(start_edit_name, pattern="^personal_edit_name$")],
        states={EDIT_NAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_name)]},
        fallbacks=[],
        per_message=False,
    ),
    ConversationHandler(
        entry_points=[CallbackQueryHandler(start_edit_email, pattern="^personal_edit_email$")],
        states={EDIT_EMAIL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_email)]},
        fallbacks=[],
        per_message=False,
    ),

    # Общий ловец остальных personal_* (оставлен как был)
    CallbackQueryHandler(handle_personal_account, pattern="^personal_"),
]
