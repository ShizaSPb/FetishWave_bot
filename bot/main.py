
# bot/main.py
import os
import logging

from telegram import Update, BotCommand, BotCommandScopeChat
from telegram.ext import Application, ContextTypes

try:
    from dotenv import load_dotenv  # optional
    load_dotenv()
except Exception:
    pass

from bot.services.logging_setup import setup_logging
from bot.services.actions import log_action
from bot.middleware.audit import audit_handler
from bot.handlers.admin_controls import handlers as admin_controls_handlers
from bot.database import notion_descriptions as desc_repo
from bot.database import notion_payment_methods as pay_repo


def get_bot_token() -> str:
    token = (
        os.getenv("BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("TG_BOT_TOKEN")
    )
    if not token:
        raise RuntimeError("Set BOT_TOKEN (or TELEGRAM_BOT_TOKEN) in environment")
    return token


async def post_init(application: Application) -> None:
    # Warmup Notion caches
    try:
        d = await desc_repo.preload_all()
        p = await pay_repo.preload_all()
        logging.getLogger("warmup").info(
            "Notion caches preloaded: descriptions=%s, payment_methods=%s", d, p
        )
    except Exception as e:
        logging.getLogger("warmup").warning("Notion preload failed: %s", e)

    # Admin-only menu
    raw = os.getenv("ADMIN_IDS", "") or ""
    ids = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
    admin_cmds = [
        BotCommand("diag_descriptions", "диагностика кэша описаний"),
        BotCommand("reload_descriptions", "перезагрузить описания"),
        BotCommand("diag_payments", "диагностика способов оплаты"),
        BotCommand("reload_payments", "перезагрузить способы оплаты"),
        BotCommand("restart", "перезапустить бота"),
    ]
    for uid in ids:
        try:
            await application.bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=uid))
            logging.getLogger("admin_menu").info("Admin menu set for %s", uid)
        except Exception as e:
            logging.getLogger("admin_menu").warning("Admin menu failed for %s: %s", uid, e)

    # Identity + sample business event
    try:
        me = await application.bot.get_me()
        logging.getLogger("startup").info("Bot started as @%s (id=%s)", me.username, me.id)
        log_action("startup", username=me.username, bot_id=me.id)
    except Exception as e:
        logging.getLogger("startup").warning("get_me failed: %s", e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.getLogger("tg.error").exception(
        "Unhandled exception while handling update=%r", update, exc_info=context.error
    )


def main() -> None:
    setup_logging(log_path=os.getenv("ACTIONS_LOG_PATH", "bot_actions.log"))

    application = (
        Application.builder()
        .token(get_bot_token())
        .post_init(post_init)
        .build()
    )

    # AUDIT handler runs first and logs commands + callbacks
    application.add_handler(audit_handler, group=-100)

    # Project handlers (if exists)
    try:
        from bot.handlers import handlers as project_handlers  # type: ignore
        for h in project_handlers:
            application.add_handler(h)
        logging.getLogger("startup").info("Project handlers registered: %s", len(project_handlers))
    except Exception as e:
        logging.getLogger("startup").info("No project handlers aggregator: %s", e)

    # Admin controls
    for h in admin_controls_handlers:
        application.add_handler(h)
    logging.getLogger("startup").info("Admin controls registered: %s", len(admin_controls_handlers))

    # Errors
    application.add_error_handler(error_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
