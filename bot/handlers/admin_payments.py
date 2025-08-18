import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from bot.utils.admin_keyboards import get_admin_payment_actions_kb, get_admin_confirm_kb

logger = logging.getLogger(__name__)

# ====== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ПАМЯТИ ======

def remember_pending_payment(context: ContextTypes.DEFAULT_TYPE, *, user_id: int, payment_type: str, product_code: str|None=None, notion_payment_id: str|None=None) -> str:
    """
    Сохраняем сведения о «висящем» платеже, чтобы затем обработать клик админа.
    Возвращаем короткий payment_id для callback_data.
    """
    from uuid import uuid4
    pid = uuid4().hex[:12]
    store = context.bot_data.setdefault("pending_payments", {})
    store[pid] = {
        "user_id": user_id,
        "payment_type": payment_type,
        "product_code": product_code,
        "notion_payment_id": notion_payment_id,
        "created_at": datetime.utcnow().isoformat()
    }
    return pid

def _get_pending(context: ContextTypes.DEFAULT_TYPE, pid: str):
    return context.bot_data.get("pending_payments", {}).get(pid)

def _pop_pending(context: ContextTypes.DEFAULT_TYPE, pid: str):
    return context.bot_data.get("pending_payments", {}).pop(pid, None)

# ====== ОБРАБОТЧИКИ КНОПОК АДМИНА ======

async def _open_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=get_admin_confirm_kb(pid))

async def _back_to_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=get_admin_payment_actions_kb(pid))

async def _approve(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    data = _get_pending(context, pid)
    if not data:
        await query.answer("Ссылка на платёж не найдена", show_alert=True)
        return

    user_id = data["user_id"]
    payment_type = data["payment_type"]

    # 1) Отметить платёж как подтверждённый (интеграция с Notion — по желанию)
    try:
        from bot.database.notion_payments import approve_payment_and_issue_access  # type: ignore
        try:
            await approve_payment_and_issue_access(
                user_telegram_id=user_id,
                admin_telegram_id=update.effective_user.id,
                payment_type=payment_type,
                notion_payment_id=data.get("notion_payment_id"),
                product_code=data.get("product_code"),
            )
        except Exception as e:
            logger.warning("Notion approval failed: %s", e)
    except Exception:
        # Модуль может отсутствовать — ок.
        pass

    # 3) Удалить сообщение у админа (только это одно)
    try:
        await query.answer("Оплата подтверждена")
    except Exception:
        pass

    try:
        # удаляем именно то сообщение, под которым нажали кнопки
        if query.message:
            await query.message.delete()
    except Exception as e:
        # если не получилось удалить (нет прав и т.п.), просто уберём клавиатуру и отметим текстом
        logger.error("Failed to delete admin message: %s", e)
        try:
            caption = (query.message.caption or "") if query.message else ""
            new_caption = caption + "\n\n✅ Оплата подтверждена."
            if query.message and query.message.caption is not None:
                await query.edit_message_caption(caption=new_caption, reply_markup=None)
            else:
                await query.edit_message_text(text=new_caption, reply_markup=None)
        except Exception as e2:
            logger.error("Failed to edit admin message: %s", e2)

    # 4) Удаляем из памяти
    _pop_pending(context, pid)

async def handle_admin_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data.startswith("adm_pay:"):
        return

    try:
        _, action, pid = query.data.split(":")
    except ValueError:
        return

    if action == "confirm":
        return await _open_confirm(update, context, pid)
    if action == "no":
        # Нет — просто вернуться к экрану с одной кнопкой "Подтвердить оплату"
        return await _back_to_actions(update, context, pid)
    if action == "yes":
        return await _approve(update, context, pid)

    await query.answer()

handlers = [
    CallbackQueryHandler(handle_admin_payment_callback, pattern=r"^adm_pay:"),
]
