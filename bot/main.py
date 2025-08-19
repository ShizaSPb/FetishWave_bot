import os
import logging
import re
import httpx

from telegram import Update, BotCommand, BotCommandScopeChat
from telegram.ext import Application, ContextTypes
from telegram.request import HTTPXRequest
from bot.services.logging_setup import setup_logging

# опционально
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# наш логгер: root → консоль+файл, JSON-события → тот же файл
# (если у тебя нет bot/utils/logger.py — скажи, кину файл)
from bot.utils.logger import setup_logging, log_action

# админ-команды и Notion-репозитории
from bot.handlers.admin_controls import handlers as admin_controls_handlers
from bot.database import notion_descriptions as desc_repo
from bot.database import notion_payment_methods as pay_repo

def main() -> None:
    setup_logging(log_path=os.getenv("ACTIONS_LOG_PATH", "bot_actions.log"))

def get_bot_token() -> str:
    token = (
        os.getenv("BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or os.getenv("TG_BOT_TOKEN")
    )
    if not token:
        raise RuntimeError("Set BOT_TOKEN (or TELEGRAM_BOT_TOKEN) in environment")
    return token


# HTTP-аудит Telegram без задержек (пишем в bot_actions.log JSON-события)
_TOKEN_MASK = re.compile(r"/bot[0-9]+:[A-Za-z0-9_-]+")
def _redact(url: str) -> str:
    return _TOKEN_MASK.sub("/bot<redacted>", url)

def build_tg_request() -> HTTPXRequest:
    async def on_request(req: httpx.Request) -> None:
        url = _redact(str(req.url))
        log_action("http_req", lib="telegram", method=req.method, url=url, host=req.url.host)

    async def on_response(resp: httpx.Response) -> None:
        req = resp.request
        url = _redact(str(req.url))
        log_action(
            "http", lib="telegram", method=req.method, url=url, host=req.url.host,
            status=resp.status_code, ok=resp.status_code < 400, status_text=resp.reason_phrase,
        )

    client = httpx.AsyncClient(event_hooks={"request": [on_request], "response": [on_response]})
    return HTTPXRequest(client=client)


async def post_init(application: Application) -> None:
    # прогрев Notion
    try:
        d = await desc_repo.preload_all()
        p = await pay_repo.preload_all()
        logging.getLogger("warmup").info(
            "Notion caches preloaded: descriptions=%s, payment_methods=%s", d, p
        )
    except Exception as e:
        logging.getLogger("warmup").warning("Notion preload failed: %s", e)

    # персональное меню для админов
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

    # кто мы
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
    # инициализируем логи: консоль + файл bot_actions.log (можно сменить путём env ACTIONS_LOG_PATH)
    setup_logging()

    application = (
        Application.builder()
        .token(get_bot_token())
        .post_init(post_init)         # прогрев/меню/идентификация безопасно внутри PTB loop
        .build()
    )

    # твои проектные хендлеры (если есть агрегатор)
    try:
        from bot.handlers import handlers as project_handlers  # type: ignore
        for h in project_handlers:
            application.add_handler(h)
        logging.getLogger("startup").info("Project handlers registered: %s", len(project_handlers))
    except Exception as e:
        logging.getLogger("startup").info("No project handlers aggregator: %s", e)

    # админ-команды
    for h in admin_controls_handlers:
        application.add_handler(h)
    logging.getLogger("startup").info("Admin controls registered: %s", len(admin_controls_handlers))

    # ошибки
    application.add_error_handler(error_handler)

    # старт
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
