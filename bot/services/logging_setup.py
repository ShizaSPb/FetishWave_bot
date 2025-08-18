
# bot/services/logging_setup.py
import os
import re
import json
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse
from typing import Optional

class JsonRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that flushes after every emit."""
    def emit(self, record: logging.LogRecord) -> None:
        super().emit(record)
        try:
            self.flush()
        except Exception:
            pass

class _ActionsJsonHandler(logging.Handler):
    """
    Bridges selected library loggers (httpx/telegram/notion) into 'actions' logger as JSON.
    Supports common 'HTTP Request: METHOD URL "HTTP/x.y CODE TEXT"' format and falls back to http_raw.
    """
    def __init__(self, actions_logger: logging.Logger) -> None:
        super().__init__()
        self.actions_logger = actions_logger
        self.req_with_status = re.compile(
            r'HTTP\s+Request:\s+(\w+)\s+(\S+)\s+\"HTTP/[^"]+\s+(\d{3})\s+([^"]+)\"'
        )
        self.req_simple = re.compile(r'HTTP\s+Request:\s+(\w+)\s+(\S+)\s*$')
        self.resp = re.compile(r'HTTP\s+Response:\s+\"HTTP/[^"]+\s+(\d{3})\s+([^"]+)\"')

    @staticmethod
    def _redact_bot_token(url: str) -> str:
        return re.sub(r'/bot[0-9]+:[A-Za-z0-9_-]+', '/bot<redacted>', url)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage() or ""
            name = record.name
            payload = None

            # Try parse Request with inline status
            m = self.req_with_status.search(msg)
            if m:
                method, url, code, status_text = m.group(1), m.group(2), int(m.group(3)), m.group(4)
                red = self._redact_bot_token(url)
                host = urlparse(red).netloc
                payload = {"event": "http", "lib": name.split('.')[0], "method": method,
                           "url": red, "host": host, "status": code, "ok": code < 400, "status_text": status_text}

            # Parse simple Request (no status on same line)
            if payload is None:
                m = self.req_simple.search(msg)
                if m:
                    method, url = m.group(1), m.group(2)
                    red = self._redact_bot_token(url)
                    host = urlparse(red).netloc
                    payload = {"event": "http_req", "lib": name.split('.')[0], "method": method,
                               "url": red, "host": host}

            # Parse Response line
            if payload is None:
                m = self.resp.search(msg)
                if m:
                    code, status_text = int(m.group(1)), m.group(2)
                    payload = {"event": "http_resp", "lib": name.split('.')[0], "status": code,
                               "ok": code < 400, "status_text": status_text}

            # Fallback
            if payload is None:
                payload = {"event": "http_raw", "lib": name, "message": msg}

            self.actions_logger.info(json.dumps(payload, ensure_ascii=False))
        except Exception:
            # never break logging
            pass

def setup_logging(level: Optional[str] = None, log_path: str = "bot_actions.log",
                  enable_http_bridge: bool = True) -> None:
    """
    Configures logging:
      - root -> stdout
      - 'actions' -> JSON lines to `log_path` (rotating, flush per line)
      - optional: bridge httpx/telegram/notion logs into 'actions' as JSON
    """
    lvl_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    lvl = getattr(logging, lvl_name, logging.INFO)

    # root -> console
    root = logging.getLogger()
    root.setLevel(lvl)
    for h in list(root.handlers):
        root.removeHandler(h)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    # actions -> file (flush each line)
    actions_logger = logging.getLogger("actions")
    actions_logger.setLevel(lvl)
    actions_logger.propagate = False
    for h in list(actions_logger.handlers):
        actions_logger.removeHandler(h)
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    fh = JsonRotatingFileHandler(log_path, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    actions_logger.addHandler(fh)

    # Quiet noisy libs a bit
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    if enable_http_bridge:
        bridge = _ActionsJsonHandler(actions_logger)

        # Attach bridge to several relevant loggers
        for lname in [
            "httpx",                       # HTTPX client
            "telegram.request",            # PTB request layer
            "telegram.ext._application",   # PTB bootstrap network loop
            "notion_client.client",        # Notion SDK
        ]:
            lg = logging.getLogger(lname)
            lg.setLevel(logging.INFO)
            lg.addHandler(bridge)
