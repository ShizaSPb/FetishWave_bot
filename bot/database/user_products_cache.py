import time
from typing import Any, Dict, List, Optional

# Простой in-memory кэш (на жизнь процесса)
_TTL_SECONDS = 60  # можно увеличить до 300
_cache: Dict[int, tuple[float, List[Dict[str, Any]]]] = {}

def get_cached(user_id: int) -> Optional[List[Dict[str, Any]]]:
    item = _cache.get(user_id)
    if not item:
        return None
    ts, data = item
    if time.time() - ts > _TTL_SECONDS:
        _cache.pop(user_id, None)
        return None
    return data

def set_cached(user_id: int, data: List[Dict[str, Any]]) -> None:
    _cache[user_id] = (time.time(), data)

def invalidate(user_id: int) -> None:
    _cache.pop(user_id, None)
