import logging
from datetime import datetime, timedelta, timezone

from notion_client import Client
from config import NOTION_TOKEN
from config import (
    NOTION_USERS_DB_ID,
    NOTION_PRODUCTS_DB_ID,
    NOTION_PAYMENTS_DB_ID,
    NOTION_PURCHASES_DB_ID,
)

logger = logging.getLogger(__name__)

_client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

def _safe_id(v):
    return v if v and isinstance(v, str) else None

def _db_ready():
    return all([
        NOTION_TOKEN,
        NOTION_USERS_DB_ID,
        NOTION_PAYMENTS_DB_ID,
    ])

async def create_payment_record(*, user_telegram_id: int, payment_type: str, proof_file_id: str, product_code: str|None=None, username: str|None=None, name: str|None=None) -> str|None:
    """
    Создаёт запись в БД Payments (если настроены ключи). Возвращает page_id или None.
    """
    if not _db_ready() or _client is None:
        return None

    try:
        # 1) Найдём (или не будем связывать) пользователя
        user_page_id = None
        try:
            res = _client.databases.query(
                database_id=NOTION_USERS_DB_ID,
                filter={"property": "Telegram ID", "number": {"equals": int(user_telegram_id)}}
            )
            if res["results"]:
                user_page_id = res["results"][0]["id"]
        except Exception as e:
            logger.warning("Users query failed: %s", e)

        # 2) Опционально найдём продукт по Slug/Code
        product_relation = []
        if _safe_id(NOTION_PRODUCTS_DB_ID) and product_code:
            try:
                r = _client.databases.query(
                    database_id=NOTION_PRODUCTS_DB_ID,
                    filter={"property": "Slug/Code", "rich_text": {"equals": product_code}}
                )
                if r["results"]:
                    product_relation = [{"id": r["results"][0]["id"]}]
            except Exception as e:
                logger.warning("Products query failed: %s", e)

        # 3) Создаём платёж
        props = {
            "Name": {"title": [{"text": {"content": f"Payment {user_telegram_id} {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]},
            "Telegram ID": {"number": int(user_telegram_id)},
            "Proof TG file_id": {"rich_text": [{"text": {"content": proof_file_id}}]},
            "Status": {"select": {"name": "submitted"}},
            "Type": {"select": {"name": payment_type}},
        }
        if user_page_id:
            props["User"] = {"relation": [{"id": user_page_id}]}
        if product_relation:
            props["Products"] = {"relation": product_relation}
        page = _client.pages.create(parent={"database_id": NOTION_PAYMENTS_DB_ID}, properties=props)
        return page["id"]
    except Exception as e:
        logger.error("Failed to create payment record: %s", e)
        return None

async def approve_payment_and_issue_access(*, user_telegram_id: int, admin_telegram_id: int, payment_type: str, notion_payment_id: str|None=None, product_code: str|None=None):
    """
    Обновляет статус платежа в Notion и (если задан продукт) создаёт Purchase с учётом Access days.
    Все поля и связи необязательны: если чего-то нет, просто обновим статус платежа.
    """
    if not _db_ready() or _client is None or notion_payment_id is None:
        return

    try:
        # Подтвердим платёж
        props = {
            "Status": {"select": {"name": "paid"}},
            "Processed at": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        }
        try:
            props["Admin"] = {"rich_text": [{"text": {"content": str(admin_telegram_id)}}]}
        except Exception:
            pass

        _client.pages.update(page_id=notion_payment_id, properties=props)

        # Если нет продукта — на этом закончим
        if not _safe_id(NOTION_PRODUCTS_DB_ID) or not _safe_id(NOTION_PURCHASES_DB_ID) or not product_code:
            return

        # Найдём пользователя и продукт
        user_page_id = None
        res = _client.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": int(user_telegram_id)}}
        )
        if res["results"]:
            user_page_id = res["results"][0]["id"]

        pr = _client.databases.query(
            database_id=NOTION_PRODUCTS_DB_ID,
            filter={"property": "Slug/Code", "rich_text": {"equals": product_code}}
        )
        if not pr["results"]:
            return
        product_page = pr["results"][0]
        product_page_id = product_page["id"]

        access_days = None
        try:
            access_days = product_page["properties"]["Access days"]["number"]
        except Exception:
            pass

        paid_at = datetime.now(timezone.utc)
        expires_at = (paid_at + timedelta(days=int(access_days))) if access_days else None

        purchase_props = {
            "Name": {"title": [{"text": {"content": f"Purchase {product_code} {user_telegram_id}"}}]},
            "Status": {"select": {"name": "paid"}},
            "Paid at": {"date": {"start": paid_at.isoformat()}},
            "Product": {"relation": [{"id": product_page_id}]},
        }
        if user_page_id:
            purchase_props["User"] = {"relation": [{"id": user_page_id}]}
        if expires_at:
            purchase_props["Expires at"] = {"date": {"start": expires_at.isoformat()}}

        purch_page = _client.pages.create(parent={"database_id": NOTION_PURCHASES_DB_ID}, properties=purchase_props)

        # Свяжем платёж и покупку
        try:
            _client.pages.update(page_id=notion_payment_id, properties={
                "Linked Purchase": {"relation": [{"id": purch_page["id"]}]}
            })
        except Exception:
            pass

    except Exception as e:
        logger.error("Failed to approve payment or issue access: %s", e)