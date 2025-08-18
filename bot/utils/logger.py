import logging
from logging.handlers import RotatingFileHandler
import json
from pathlib import Path
from datetime import datetime

LOG_FILE = Path(__file__).parent.parent.parent / "bot_actions.log"


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return True


def setup_logging():
    """Настройка системы логирования с выводом и в файл, и в консоль"""
    LOG_FILE.parent.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        '%(timestamp)s | %(levelname)-8s | %(name)-25s | %(message)s'
    )

    # Обработчик для файла
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(ContextFilter())

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(ContextFilter())

    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)  # Добавляем вывод в консоль


def log_action(action: str, user_id: int = None, metadata: dict = None):
    """Логирование действий"""
    logger = logging.getLogger('bot.actions')
    log_data = {
        "action": action,
        "user_id": user_id,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    logger.info(json.dumps(log_data, ensure_ascii=False))