
# bot/handlers/admin_payments.py (no user notify on approve)
"""
Изменение: после подтверждения оплаты НИЧЕГО не отправляем пользователю.
Оставлена только всплывашка админу и удаление админского сообщения.
"""
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from bot.utils.admin_keyboards import get_admin_payment_actions_kb, get_admin_confirm_kb

logger = logging.getLogger(__name__)

# ====== ПАМЯТЬ ======
def remember_pending_payment(context: ContextTypes.DEFAULT_TYPE, *, payment_id: str|int|None=None, user_id: int|None=None, payment_type: str|None=None, product_code: str|None=None, notion_payment_id: str|None=None) -> str:
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

# ====== КНОПКИ АДМИНА ======
async def _open_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=get_admin_confirm_kb(pid))
    except Exception as e:
        logger.error("Failed to show confirm kb: %s", e)

async def _back_to_actions(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_reply_markup(reply_markup=get_admin_payment_actions_kb(pid))
    except Exception as e:
        logger.error("Failed to show actions kb: %s", e)

async def _approve(update: Update, context: ContextTypes.DEFAULT_TYPE, pid: str):
    query = update.callback_query
    data = _get_pending(context, pid)

    # Вариант 1: запись в памяти отсутствует — разбираем payload "<notion_id>|<user_id>"
    if not data:
        notion_id = None
        user_id = None
        if '|' in pid:
            parts = pid.split('|', 1)
            notion_id = parts[0] or None
            try:
                user_id = int(parts[1])
            except Exception:
                user_id = None

        if notion_id and user_id:
            try:
                from bot.database.notion_payments import approve_payment_and_issue_access  # type: ignore
                try:
                    await approve_payment_and_issue_access(
                        user_telegram_id=user_id,
                        admin_telegram_id=getattr(update.effective_user, "id", None),
                        notion_payment_id=notion_id,
                        product_code=None,
                    )
                except TypeError:
                    # совместимость старых сигнатур
                    await approve_payment_and_issue_access(
                        user_telegram_id=user_id,
                        notion_payment_id=notion_id,
                    )
            except Exception as e:
                logger.warning("Notion approval (fallback) failed: %s", e)
        else:
            await query.answer("Ссылка на платёж не найдена", show_alert=True)
            return
    else:
        user_id = data["user_id"]
        payment_type = data["payment_type"]
        notion_id = data.get("notion_payment_id")

        # 1) Отметить платёж как подтверждённый в Notion (если есть id)
        if notion_id:
            try:
                from bot.database.notion_payments import approve_payment_and_issue_access  # type: ignore
                try:
                    await approve_payment_and_issue_access(
                        user_telegram_id=user_id,
                        admin_telegram_id=getattr(update.effective_user, "id", None),
                        notion_payment_id=notion_id,
                        product_code=payment_type or data.get("product_code"),
                    )
                except TypeError:
                    await approve_payment_and_issue_access(
                        user_telegram_id=user_id,
                        notion_payment_id=notion_id,
                    )
            except Exception as e:
                logger.warning("Notion approval failed: %s", e)

    # Сообщения пользователю НЕ отправляем.
    # Показываем только короткое уведомление админу и удаляем сообщение с кнопками.
    try:
        await query.answer("Оплата подтверждена")
    except Exception:
        pass
    try:
        if query.message:
            await query.message.delete()
    except Exception as e:
        logger.error("Failed to delete admin message: %s", e)

async def handle_admin_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = (query.data or "")
    try:
        _, action, pid = data.split(":", 2)
    except ValueError:
        await query.answer()
        return

    if action == "confirm":
        return await _open_confirm(update, context, pid)
    if action == "no":
        return await _back_to_actions(update, context, pid)
    if action == "yes":
        return await _approve(update, context, pid)

    await query.answer()

handlers = [
    CallbackQueryHandler(handle_admin_payment_callback, pattern=r"^adm_pay:"),
]
