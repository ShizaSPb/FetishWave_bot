# bot/utils/cb_store.py
import time
import secrets
import base64
import threading
from typing import Dict, Tuple, Any, Optional

class CbStore:
    def __init__(self, ttl_seconds: int = 60 * 60 * 48, max_items: int = 5000):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self._data: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._lock = threading.Lock()

    def _cleanup(self):
        now = time.time()
        dead = [k for k, (_, exp) in self._data.items() if exp < now]
        for k in dead:
            self._data.pop(k, None)
        if len(self._data) > self.max_items:
            for k, _ in sorted(self._data.items(), key=lambda kv: kv[1][1])[:len(self._data) - self.max_items]:
                self._data.pop(k, None)

    def put(self, payload: Dict[str, Any], ttl: Optional[int] = None, key: Optional[str] = None) -> str:
        with self._lock:
            self._cleanup()
            if key is None:
                key = base64.urlsafe_b64encode(secrets.token_bytes(8)).decode().rstrip("=").lower()
            exp = time.time() + (ttl if ttl is not None else self.ttl)
            self._data[key] = (payload, exp)
            return key

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            item = self._data.get(key)
            if not item:
                return None
            payload, exp = item
            if exp < time.time():
                self._data.pop(key, None)
                return None
            return payload

cb_store = CbStore()
