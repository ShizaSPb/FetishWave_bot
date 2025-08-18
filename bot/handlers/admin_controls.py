
import os, sys, signal, asyncio, subprocess
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.utils.admins import is_admin
from bot.database import notion_descriptions as desc_repo
from bot.database import notion_payment_methods as pay_repo
from bot.services.actions import log_action

async def _ensure_admin(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else None
    if not uid or not is_admin(uid):
        await update.effective_chat.send_message("⛔ Доступ запрещён.")
        return False
    return True

# -------- DIAG/RELOAD FOR DESCRIPTIONS --------
async def diag_descriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    info = desc_repo.cache_info()
    log_action("admin_diag_descriptions", user_id=update.effective_user.id, cache_info=info)
    await update.effective_chat.send_message(
        f"🧠 Descriptions cache: keys={info.get('keys')} age_min={info.get('min_age_sec'):.1f}s age_max={info.get('max_age_sec'):.1f}s"
    )

async def reload_descriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    try:
        count = await desc_repo.reload()
        log_action("admin_reload_descriptions", user_id=update.effective_user.id, count=count)
        await update.effective_chat.send_message(f"♻️ Descriptions reloaded: {count} items.")
    except Exception as e:
        log_action("admin_reload_descriptions_error", user_id=update.effective_user.id, error=str(e))
        await update.effective_chat.send_message(f"❌ Reload failed: {e}")

# -------- DIAG/RELOAD FOR PAYMENT METHODS --------
async def diag_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    info = pay_repo.cache_info()
    methods = await pay_repo.get_all()
    log_action("admin_diag_payments", user_id=update.effective_user.id, methods=len(methods), cache_info=info)
    lines = [f"🧠 Payment methods cache: keys={info.get('keys')}"]
    for m in methods[:25]:
        lines.append(f"• {m.get('code')} [{m.get('currency')}], rate={m.get('rate_per_eur')}, round_to={m.get('round_to')}")
    if len(methods) > 25:
        lines.append(f"... and {len(methods)-25} more")
    await update.effective_chat.send_message("\n".join(lines))

async def reload_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    try:
        count = await pay_repo.reload()
        log_action("admin_reload_payments", user_id=update.effective_user.id, count=count)
        await update.effective_chat.send_message(f"♻️ Payment methods reloaded: {count} items.")
    except Exception as e:
        log_action("admin_reload_payments_error", user_id=update.effective_user.id, error=str(e))
        await update.effective_chat.send_message(f"❌ Reload failed: {e}")

# -------- RESTART --------
async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да, перезапустить", callback_data="adm:restart:yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="adm:restart:no")],
    ])
    # try to remove the /restart command message to keep chat clean
    try:
        if update.effective_message:
            await update.effective_message.delete()
    except Exception:
        pass
    msg = await update.effective_chat.send_message("Перезапустить процесс бота?", reply_markup=kb)
    log_action("admin_restart_prompt", user_id=update.effective_user.id, message_id=msg.message_id)

def _spawn_new_process() -> None:
    python = sys.executable
    args = [python, "-m", "bot.main"]
    try:
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        subprocess.Popen(args, close_fds=False, creationflags=creationflags)
    except Exception:
        subprocess.Popen(args, close_fds=False)

async def restart_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure_admin(update): return
    q = update.callback_query
    if not q:
        return
    await q.answer()
    data = q.data or ""
    if data.endswith(":no"):
        try:
            await q.message.delete()
        except Exception:
            pass
        await update.effective_chat.send_message("Отменено.")
        log_action("admin_restart_cancel", user_id=update.effective_user.id)
        return

    # YES: remove confirmation message and show short notice that will also be removed
    try:
        await q.message.delete()
    except Exception:
        pass
    try:
        tmp = await update.effective_chat.send_message("Перезапускаюсь…")
    except Exception:
        tmp = None

    log_action("admin_restart_confirm", user_id=update.effective_user.id)

    await asyncio.sleep(0.3)
    if tmp:
        try:
            await tmp.delete()
        except Exception:
            pass

    mode = os.getenv("SELF_RESTART", "1")
    if mode == "1":
        _spawn_new_process()
        os._exit(0)
    else:
        try:
            os.kill(os.getpid(), signal.SIGTERM)
        except Exception:
            os._exit(0)

handlers: List = [
    CommandHandler("diag_descriptions", diag_descriptions),
    CommandHandler("reload_descriptions", reload_descriptions),
    CommandHandler("diag_payments", diag_payments),
    CommandHandler("reload_payments", reload_payments),
    CommandHandler("restart", restart_cmd),
    CallbackQueryHandler(restart_cb, pattern=r"^adm:restart:(yes|no)$"),
]

handler = handlers
