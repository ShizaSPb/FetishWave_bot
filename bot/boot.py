# bot/boot.py
"""
Применяем совместимость для старых позиционных вызовов log_action максимально рано.
Этот модуль нужно импортировать ДО импорта любых хендлеров.
"""
from __future__ import annotations

try:
    from bot.services.actions_compat import patch_log_action_positional  # type: ignore
    patch_log_action_positional()
except Exception:
    # Безопасный no-op — запуск бота из-за этого не должен падать
    pass
