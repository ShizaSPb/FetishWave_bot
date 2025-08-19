import pytest
import logging
import json
import os
from pathlib import Path
from unittest.mock import patch

# Важно: используем абсолютные импорты
from bot.services.logging_setup import setup_logging
from services.actions import log_action


@pytest.fixture
def temp_log_file(tmp_path):
    """Создает временный лог-файл для тестов"""
    log_file = tmp_path / "test.log"
    return log_file


@pytest.fixture
def configured_logger(temp_log_file):
    """Настраивает логгер с временным файлом"""
    original_path = None

    # Монтируем патч для LOG_FILE
    with patch('bot.utils.logger.LOG_FILE', temp_log_file):
        setup_logging()
        yield

    # Очищаем хендлеры после теста
    logging.getLogger().handlers.clear()


def test_logging_levels(configured_logger, temp_log_file):
    logger = logging.getLogger("test.module")
    test_msg = "Test logging message"

    logger.info(test_msg)
    logger.error(test_msg)

    log_content = temp_log_file.read_text()

    assert "INFO | test.module" in log_content
    assert "ERROR | test.module" in log_content
    assert test_msg in log_content


def test_log_action_format(configured_logger, temp_log_file):
    log_action("test_action", 123, {"key": "value"})

    log_content = temp_log_file.read_text()
    log_line = [line for line in log_content.splitlines() if "test_action" in line][0]

    # Проверяем JSON часть лога
    json_part = log_line.split("|")[-1].strip()
    log_data = json.loads(json_part)

    assert log_data["action"] == "test_action"
    assert log_data["user_id"] == 123
    assert log_data["metadata"] == {"key": "value"}