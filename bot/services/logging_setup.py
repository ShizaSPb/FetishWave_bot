import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(level: str | None = None, log_path: str = "bot_actions.log") -> None:
    """
    Configures logging so that:
      - console logs go to stdout
      - business events go to file `bot_actions.log` (rotating, 5MB, 3 backups)
    Call this once at startup.

    Args:
        level: override log level (default comes from LOG_LEVEL env or INFO)
        log_path: path to bot_actions.log (relative to working dir by default)
    """
    lvl_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    lvl = getattr(logging, lvl_name, logging.INFO)

    # --- root logger (console) ---
    root = logging.getLogger()
    root.setLevel(lvl)
    # clear existing handlers to avoid duplicates on restart
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)

    # --- dedicated 'actions' logger (file) ---
    actions_logger = logging.getLogger("actions")
    actions_logger.setLevel(lvl)
    actions_logger.propagate = False  # don't duplicate to console

    for h in list(actions_logger.handlers):
        actions_logger.removeHandler(h)

    # ensure parent dir exists (if a path like logs/bot_actions.log is given)
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)

    fh = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    actions_logger.addHandler(fh)

    # make noisy libs quieter if needed
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("telegram").setLevel(logging.INFO)
