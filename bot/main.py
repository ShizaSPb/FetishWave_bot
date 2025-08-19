from __future__ import annotations

# ВАЖНО: включаем совместимость log_action максимально рано
import bot.boot  # noqa: F401
import asyncio
import logging
import os
from typing import List
from telegram.ext import Application
from bot.services.logging_setup import setup_logging
from bot.services.actions import log_action

try:
    from config import ADMIN_IDS  # type: ignore
except Exception:
    ADMIN_IDS: List[int] = []

# Обработчик ошибок (безопасный)
try:
    from bot.handlers.errors import error_handler  # type: ignore
except Exception:
    error_handler = None  # необязательно


def _register_project_handlers(application: Application) -> int:
    count = 0
    try:
        from bot.handlers import handlers as project_handlers  # type: ignore
        for h in project_handlers:
            application.add_handler(h)
            count += 1
    except Exception:
        pass
    return count


def _register_payment_ack_handler(application: Application) -> None:
    from bot.handlers.payments_ackpatch import handler as payment_ack_handler  # type: ignore
    application.add_handler(payment_ack_handler)


async def _warmup(application: Application) -> None:
    log_warm = logging.getLogger("warmup")
    try:
        from bot.services.warmup import preload_notion_caches  # type: ignore
        res = await preload_notion_caches()
        if isinstance(res, dict):
            log_warm.info("Notion caches preloaded: %s", ", ".join(f"{k}={v}" for k, v in res.items()))
        else:
            log_warm.info("Notion caches preloaded")
    except Exception:
        pass


async def _setup_admin_controls(application: Application) -> None:
    log_admin = logging.getLogger("admin_menu")
    try:
        from bot.handlers.admin_menu import install_admin_menu  # type: ignore
        for admin_id in ADMIN_IDS:
            try:
                await install_admin_menu(application.bot, admin_id)  # type: ignore[arg-type]
                log_admin.info("Admin menu set for %s", admin_id)
            except Exception:
                logging.getLogger(__name__).exception("Failed to set admin menu for %s", admin_id)
    except Exception:
        pass

    try:
        from telegram import BotCommand
        await application.bot.set_my_commands([
            BotCommand("start", "Главное меню"),
            BotCommand("help", "Помощь"),
        ])
        logging.getLogger("startup").info("Default bot commands set")
    except Exception:
        pass


async def _on_startup(application: Application) -> None:
    log_start = logging.getLogger("startup")
    try:
        me = await application.bot.get_me()
    except Exception as e:
        log_start.warning("get_me failed: %s", e)
    else:
        log_start.info("Bot started as @%s (id=%s)", me.username, me.id)
        try:
            log_action("startup", username=me.username, bot_id=me.id)
        except Exception:
            pass

    await _warmup(application)
    await _setup_admin_controls(application)


async def _on_shutdown(application: Application) -> None:
    logging.getLogger("startup").info("Application is stopping. This might take a moment.")
    try:
        log_action("shutdown")
    except Exception:
        pass


def _get_token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задан токен бота. Укажи TELEGRAM_BOT_TOKEN или BOT_TOKEN.")
    return token


async def main() -> None:
    setup_logging()

    application = (
        Application.builder()
        .token(_get_token())
        .concurrent_updates(True)
        .build()
    )

    count = _register_project_handlers(application)
    logging.getLogger("startup").info("Project handlers registered: %s", count)

    _register_payment_ack_handler(application)

    if error_handler:
        application.add_error_handler(error_handler)

    await application.initialize()
    await application.start()
    await _on_startup(application)
    await application.updater.start_polling(drop_pending_updates=True)

    try:
        await asyncio.Event().wait()  # держим процесс
    except asyncio.CancelledError:
        pass  # ожидаемая отмена при Ctrl+C
    finally:
        # корректное завершение PTB
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
