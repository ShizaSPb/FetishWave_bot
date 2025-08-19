import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
ADMIN_IDS = int(os.getenv("ADMIN_IDS"))

# IDs отдельных БД в Notion — укажите при желании автоматизировать подтверждение
NOTION_USERS_DB_ID = os.getenv("NOTION_USERS_DB_ID")            # Users
NOTION_PRODUCTS_DB_ID = os.getenv("NOTION_PRODUCTS_DB_ID")      # Products
NOTION_PAYMENTS_DB_ID = os.getenv("NOTION_PAYMENTS_DB_ID")      # Payments
NOTION_PURCHASES_DB_ID = os.getenv("NOTION_PURCHASES_DB_ID")    # Purchases


def _parse_admin_ids(raw: str) -> List[int]:
    """
    Поддержка форматов:
      - "158087136,123456789"
      - "158087136; 123456789"
      - "158087136 | 123456789"
    Всё, что не int — игнорируем.
    """
    if not raw:
        return []
    ids: List[int] = []
    for part in raw.replace(";", ",").replace("|", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            pass
    return ids

# Основной источник — переменная окружения ADMIN_IDS
ADMIN_IDS: List[int] = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))

# Обратная совместимость: если раньше был только ADMIN_CHAT_ID — тоже учитываем
_admin_chat_id = os.getenv("ADMIN_CHAT_ID")
if _admin_chat_id:
    try:
        one = int(_admin_chat_id)
        if one not in ADMIN_IDS:
            ADMIN_IDS.append(one)
    except ValueError:
        pass