
import time
from typing import Any, Dict, Optional, Tuple

class TTLCache:
    """
    Very small in-memory TTL cache. Not thread-safe (simple use in single-process bot).
    """
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl = ttl_seconds
        self._data: Dict[str, Tuple[float, Any]] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = (time.time(), value)

    def get(self, key: str) -> Optional[Any]:
        item = self._data.get(key)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > self.ttl:
            self._data.pop(key, None)
            return None
        return val

    def clear(self) -> None:
        self._data.clear()

    def info(self) -> Dict[str, Any]:
        # returns counts and age stats (lightweight)
        now = time.time()
        ages = []
        for ts, _ in self._data.values():
            ages.append(now - ts)
        return {
            "keys": len(self._data),
            "max_age_sec": max(ages) if ages else 0.0,
            "min_age_sec": min(ages) if ages else 0.0,
        }
