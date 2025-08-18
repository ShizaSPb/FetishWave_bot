import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from notion_client import Client
from config import (
    NOTION_TOKEN,
    NOTION_USERS_DB_ID,
    NOTION_PURCHASES_DB_ID,
    NOTION_PRODUCTS_DB_ID,
    NOTION_PAYMENTS_DB_ID,
)

from .user_products_cache import get_cached, set_cached

logger = logging.getLogger(__name__)
client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

def _clean_id(v):
    return v if v and isinstance(v, str) else None

def _ready() -> bool:
    return bool(NOTION_TOKEN and client is not None and (_clean_id(NOTION_PAYMENTS_DB_ID) or _clean_id(NOTION_PURCHASES_DB_ID)))

def _iso_to_dt(s: str):
    if not s:
        return None
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _get_user_page(telegram_id: int) -> str | None:
    if not _clean_id(NOTION_USERS_DB_ID):
        return None
    try:
        u = client.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": int(telegram_id)}}
        )
        if u["results"]:
            return u["results"][0]["id"]
    except Exception as e:
        logger.warning("Users lookup failed: %s", e)
    return None

def _read_payment_fast(row: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Быстрый путь: читаем из Payments предзаполненные поля 'Product Name' и 'Expires at'.
    Никаких дополнительных запросов к Notion.
    """
    props = row.get("properties", {})
    name = None
    try:
        rt = props.get("Product Name", {}).get("rich_text", [])
        if rt:
            name = "".join([(s.get("plain_text") or s.get("text", {}).get("content", "")) for s in rt]).strip()
    except Exception:
        pass
    if not name:
        # fallback: попробуем через Title Name, если вы его стали дублировать
        try:
            name = props.get("Name", {}).get("title", [{}])[0].get("plain_text")
        except Exception:
            name = None

    expires = None
    try:
        dt = props.get("Expires at", {}).get("date", {}).get("start")
        expires = _iso_to_dt(dt)
    except Exception:
        pass

    if name:
        return {"name": name, "expires_at": expires}
    return None

async def list_user_products(user_telegram_id: int):
    """
    Возвращает список активных продуктов пользователя.
    Приоритет: быстрый путь по Payments -> (опционально) Purchases как fallback.
    """
    # 0) Кэш
    cached = get_cached(user_telegram_id)
    if cached is not None:
        return cached

    if not _ready():
        return []

    user_page_id = _get_user_page(user_telegram_id)

    items: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    # 1) FAST PATH: Payments с уже записанными 'Product Name' и 'Expires at'
    if _clean_id(NOTION_PAYMENTS_DB_ID):
        try:
            or_conditions = [{"property": "Telegram ID", "number": {"equals": int(user_telegram_id)}}]
            if user_page_id:
                or_conditions.append({"property": "User", "relation": {"contains": user_page_id}})
            payments_filter = {
                "and": [
                    {"property": "Status", "select": {"equals": "paid"}},
                    {"or": or_conditions},
                ]
            }
            res = client.databases.query(database_id=NOTION_PAYMENTS_DB_ID, filter=payments_filter)
            for row in res["results"]:
                it = _read_payment_fast(row)
                if not it:
                    continue
                exp = it["expires_at"]
                if exp and exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if exp and exp < now:
                    continue
                items.append({"name": it["name"], "expires_at": exp})
        except Exception as e:
            logger.error("Payments fast-path failed: %s", e)

    # 2) (Опционально) fallback на Purchases, если ничего не нашли в Payments
    if not items and _clean_id(NOTION_PURCHASES_DB_ID):
        try:
            pr = client.databases.query(
                database_id=NOTION_PURCHASES_DB_ID,
                filter={
                    "and": [
                        {"property": "Status", "select": {"equals": "paid"}},
                        *([{"property": "User", "relation": {"contains": user_page_id}}] if user_page_id else [])
                    ]
                }
            )
            for row in pr["results"]:
                props = row.get("properties", {})
                # ожидаем, что тут тоже есть предрасчитанная дата (Expires at) и rollup имени продукта
                name = None
                try:
                    roll = props.get("Product Name", {}).get("rollup", {}).get("array", [])
                    if roll and roll[0].get("type") == "title":
                        name = roll[0]["title"][0]["plain_text"]
                except Exception:
                    pass
                if not name:
                    # fallback: возьмём просто текст названия покупки
                    try:
                        name = props.get("Name", {}).get("title", [{}])[0].get("plain_text")
                    except Exception:
                        name = None

                exp = None
                try:
                    dt = props.get("Expires at", {}).get("date", {}).get("start")
                    exp = _iso_to_dt(dt)
                except Exception:
                    pass

                if name:
                    if exp and exp.tzinfo is None:
                        exp = exp.replace(tzinfo=timezone.utc)
                    if exp and exp < now:
                        continue
                    items.append({"name": name, "expires_at": exp})
        except Exception as e:
            logger.error("Purchases fallback failed: %s", e)

    # 3) сортировка и кэширование
    items.sort(key=lambda x: x["name"].lower())
    set_cached(user_telegram_id, items)
    return items
