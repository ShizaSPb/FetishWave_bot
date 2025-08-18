# bot/handlers/cabinet_products.py
import logging
from datetime import timezone
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, ContextTypes

from bot.database.notion_user_products import list_user_products
from bot.utils.user_keyboards import get_only_back_kb

# Мы не вызываем show_personal_account, чтобы оно случайно не отправило новое сообщение.
# Рисуем ЛК сами через get_personal_account_keyboard.
from bot.utils.keyboards import get_personal_account_keyboard
from bot.utils.languages import LANGUAGES

log = logging.getLogger(__name__)

def _fmt_expiry(dt):
    if not dt:
        return "бессрочно"
    try:
        return "до " + dt.astimezone(timezone.utc).strftime("%d.%m.%Y")
    except Exception:
        return "до " + str(dt)

async def _render_products_text(user_id: int) -> str:
    try:
        items = await list_user_products(user_id)
    except Exception as e:
        log.error("list_user_products failed: %s", e)
        items = []

    if not items:
        return "У вас пока нет активных продуктов."
    lines = [f"{idx}. {p['name']} ({_fmt_expiry(p['expires_at'])})" for idx, p in enumerate(items, start=1)]
    return "Мои продукты:\n\n" + "\n".join(lines)

async def open_personal_purchases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Быстрый "загрузка..." (мгновенная реакция)
    try:
        await q.edit_message_text("⏳ Загружаю продукты...", reply_markup=get_only_back_kb(), disable_web_page_preview=True)
    except BadRequest:
        pass

    text = await _render_products_text(q.from_user.id)
    kb = get_only_back_kb()

    # Обновляем тем же сообщением на финальный контент
    try:
        await q.edit_message_text(text=text, reply_markup=kb, disable_web_page_preview=True)
        log.info('open_personal_purchases: updated with data')
        return
    except BadRequest as e:
        log.info("open_personal_purchases: second edit failed (%s), fallback to send+delete", e)

    # Фолбэк: отправим новое и удалим старое
    try:
        await context.bot.send_message(chat_id=q.message.chat.id, text=text, reply_markup=kb, disable_web_page_preview=True)
        try:
            await q.message.delete()
        except Exception:
            pass
    except Exception as e:
        log.warning("open_personal_purchases: send fallback failed: %s", e)

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # Пытаемся отредактировать текущее сообщение на экран ЛК и НИЧЕГО не удаляем при успехе
    try:
        lang = (context.user_data.get("language") or "ru")
    except Exception:
        lang = "ru"
    try:
        kb = get_personal_account_keyboard(lang)
    except Exception:
        kb = None
    title = None
    try:
        title = LANGUAGES[lang].get("personal_account_title")
    except Exception:
        pass
    if not title:
        title = "Личный кабинет"

    try:
        await q.edit_message_text(text=title, reply_markup=kb, disable_web_page_preview=True)
        log.info("go_back: edited in place to personal account")
        return
    except BadRequest as e:
        log.info("go_back: edit in place failed (%s). Will try send without deleting.", e)

    # Последний шанс: отправим новое сообщение, НО НИЧЕГО не удаляем (лучше дубликат, чем исчезновение)
    try:
        await context.bot.send_message(chat_id=q.message.chat.id, text=title, reply_markup=kb)
        log.info("go_back: sent new personal account message (no delete)")
        return
    except Exception as e:
        log.error("go_back: failed to send personal account: %s", e)

handlers = [
    CallbackQueryHandler(open_personal_purchases, pattern=r"^(cab:products|personal_purchases)$"),
    CallbackQueryHandler(go_back, pattern=r"^cab:back$"),
]
