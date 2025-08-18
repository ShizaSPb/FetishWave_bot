import logging
from notion_client import Client
from config import NOTION_TOKEN, NOTION_USERS_DB_ID

logger = logging.getLogger(__name__)
_client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

def _ready():
    return bool(NOTION_TOKEN and NOTION_USERS_DB_ID and _client is not None)

def normalize_email(email: str) -> str:
    # базовая нормализация: трим и нижний регистр
    return (email or "").strip().lower()

async def find_user_by_email(email: str):
    """Вернёт страницу пользователя по Email (точное совпадение), либо None."""
    if not _ready() or not email:
        return None
    e = normalize_email(email)
    try:
        # Пытаемся искать как email-property
        res = _client.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Email", "email": {"equals": e}}
        )
        if res["results"]:
            return res["results"][0]
        # Фолбэк: если тип Email вдруг rich_text
        res = _client.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Email", "rich_text": {"equals": e}}
        )
        if res["results"]:
            return res["results"][0]
    except Exception as ex:
        logger.error("find_user_by_email failed: %s", ex)
    return None

def _get_prop_number(page: dict, prop: str):
    try:
        return page["properties"][prop]["number"]
    except Exception:
        return None

async def email_is_free(email: str, current_telegram_id: int) -> bool:
    """Проверяет, свободен ли email. Свободен, если нет записи ИЛИ запись привязана к текущему TG ID."""
    page = await find_user_by_email(email)
    if not page:
        return True
    tg_in_db = _get_prop_number(page, "Telegram ID")
    return tg_in_db in (None, int(current_telegram_id))

async def get_existing_user_telegram_id(email: str):
    page = await find_user_by_email(email)
    if not page:
        return None
    return _get_prop_number(page, "Telegram ID")
