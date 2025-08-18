import logging
import json
from typing import Any

_logger = logging.getLogger("actions")

def log_action(event: str, **fields: Any) -> None:
    """
    Lightweight structured event logger.
    Usage:
        log_action("purchase_created", user_id=123, product="hypno_part_1", amount=99.0, currency="EUR")
    """
    try:
        payload = {"event": event, **fields}
        _logger.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        # Never crash on logging
        _logger.info(f"{event} | {fields}")
