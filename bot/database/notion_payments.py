# bot/database/notion_payments.py
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

from bot.utils.product_codes import type_to_slug

# Инвалидация кэша (если модуль установлен). Не критично.
try:
    from .user_products_cache import invalidate as invalidate_user_products_cache  # type: ignore
except Exception:
    def invalidate_user_products_cache(_uid: int):  # type: ignore
        pass

logger = logging.getLogger(__name__)
_client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

PRODUCT_NAME_PROP = "Product Name"
EXPIRES_AT_PROP = "Expires at"

def _safe_id(v):
    return v if v and isinstance(v, str) else None

def _db_ready():
    return bool(NOTION_TOKEN and NOTION_PAYMENTS_DB_ID and _client is not None)

def _get_product_page_by_slug(slug: str):
    if not _safe_id(NOTION_PRODUCTS_DB_ID) or not slug or _client is None:
        return None
    try:
        r = _client.databases.query(
            database_id=NOTION_PRODUCTS_DB_ID,
            filter={"property": "Slug/Code", "rich_text": {"equals": slug}}
        )
        if r["results"]:
            return r["results"][0]
    except Exception as e:
        logger.warning("Products query failed for slug %s: %s", slug, e)
    return None

def _get_user_page_by_tg(telegram_id: int):
    if not _safe_id(NOTION_USERS_DB_ID):
        return None
    try:
        r = _client.databases.query(
            database_id=NOTION_USERS_DB_ID,
            filter={"property": "Telegram ID", "number": {"equals": int(telegram_id)}}
        )
        if r["results"]:
            return r["results"][0]["id"]
    except Exception as e:
        logger.warning("Users query by telegram id failed: %s", e)
    return None

def _ensure_fast_fields_exist():
    """Гарантирует наличие свойств PRODUCT_NAME_PROP (rich_text) и EXPIRES_AT_PROP (date) в БД Payments."""
    try:
        db = _client.databases.retrieve(NOTION_PAYMENTS_DB_ID)
        props = db.get("properties", {}) or {}
        need_update = {}
        if PRODUCT_NAME_PROP not in props:
            need_update[PRODUCT_NAME_PROP] = {"rich_text": {}}
        if EXPIRES_AT_PROP not in props:
            need_update[EXPIRES_AT_PROP] = {"date": {}}
        if need_update:
            _client.databases.update(NOTION_PAYMENTS_DB_ID, properties=need_update)
            logger.info("Added missing properties to Payments DB: %s", ", ".join(need_update.keys()))
    except Exception as e:
        logger.warning("Failed to ensure fast fields exist: %s", e)

def _set_payment_products_relation(payment_page_id: str, product_page_id: str):
    try:
        _client.pages.update(page_id=payment_page_id, properties={
            "Products": {"relation": [{"id": product_page_id}]}
        })
        return True
    except Exception as e:
        logger.warning("Failed to set Products relation on Payment %s: %s", payment_page_id, e)
        return False

def _set_payment_fast_fields(payment_page_id: str, *, product_name: str|None, expires_at_iso: str|None):
    """Заполняем быстрые поля на самой странице Payments."""
    _ensure_fast_fields_exist()
    props = {}
    if product_name:
        props[PRODUCT_NAME_PROP] = {"rich_text": [{"text": {"content": product_name}}]}
    if expires_at_iso:
        props[EXPIRES_AT_PROP] = {"date": {"start": expires_at_iso}}
    if not props:
        return
    try:
        _client.pages.update(page_id=payment_page_id, properties=props)
    except Exception as e:
        logger.warning("Failed to set fast fields on Payment %s: %s", payment_page_id, e)

def _get_payment_type_value(payment_page: dict) -> str | None:
    t = payment_page.get("properties", {}).get("Type")
    if not isinstance(t, dict):
        return None
    if t.get("select"):
        return t["select"].get("name")
    if t.get("rich_text"):
        parts = []
        for s in t["rich_text"]:
            parts.append(s.get("plain_text") or s.get("text", {}).get("content", ""))
        return "".join(parts).strip() or None
    return None

async def create_payment_record(*, user_telegram_id: int, payment_type: str, proof_file_id: str, product_code: str|None=None, username: str|None=None, name: str|None=None) -> str|None:
    """Создаёт Payment c каноническим Type, Products и мгновенно записывает Product Name (если найден продукт)."""
    if not _db_ready():
        return None

    # Гарантируем наличие быстрых полей на уровне БД
    _ensure_fast_fields_exist()

    # Канонизируем тип до slug
    slug = product_code or type_to_slug(payment_type)
    canonical_type = slug or payment_type

    # Relations
    product_relation = []
    product_page = None
    product_name = None
    if slug:
        product_page = _get_product_page_by_slug(slug)
        if product_page:
            product_relation = [{"id": product_page["id"]}]
            try:
                product_name = product_page["properties"]["Name"]["title"][0]["plain_text"]
            except Exception:
                product_name = None

    user_page_id = _get_user_page_by_tg(user_telegram_id)

    # Properties
    props = {
        "Name": {"title": [{"text": {"content": f"Payment {user_telegram_id} {datetime.now().strftime('%Y-%m-%d %H:%M')}"}}]},
        "Telegram ID": {"number": int(user_telegram_id)},
        "Proof TG file_id": {"rich_text": [{"text": {"content": proof_file_id}}]},
        "Status": {"select": {"name": "submitted"}},
    }

    # Type kind
    try:
        db = _client.databases.retrieve(NOTION_PAYMENTS_DB_ID)
        type_kind = db.get("properties", {}).get("Type", {}).get("type")
    except Exception:
        type_kind = None
    if type_kind == "select":
        props["Type"] = {"select": {"name": canonical_type}}
    else:
        props["Type"] = {"rich_text": [{"text": {"content": canonical_type}}]}

    if user_page_id:
        props["User"] = {"relation": [{"id": user_page_id}]}
    if product_relation:
        props["Products"] = {"relation": product_relation}
    if product_name:
        props[PRODUCT_NAME_PROP] = {"rich_text": [{"text": {"content": product_name}}]}

    try:
        page = _client.pages.create(parent={"database_id": NOTION_PAYMENTS_DB_ID}, properties=props)
        return page["id"]
    except Exception as e:
        logger.error("Failed to create payment record: %s", e)
        return None

async def approve_payment_and_issue_access(*, user_telegram_id: int, admin_telegram_id: int, payment_type: str, notion_payment_id: str|None=None, product_code: str|None=None):
    """Mark payment paid, ensure Products relation, set fast fields (Product Name/Expires), invalidate cache, create Purchases."""
    if not _db_ready() or notion_payment_id is None:
        return

    # Обеспечим быстрые поля
    _ensure_fast_fields_exist()

    # 1) Mark paid + processed at + admin
    try:
        props = {
            "Status": {"select": {"name": "paid"}},
            "Processed at": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
        }
        try:
            props["Admin"] = {"rich_text": [{"text": {"content": str(admin_telegram_id)}}]}
        except Exception:
            pass
        _client.pages.update(page_id=notion_payment_id, properties=props)
    except Exception as e:
        logger.error("Failed to update payment status: %s", e)

    # 2) Retrieve payment page
    try:
        payment_page = _client.pages.retrieve(notion_payment_id)
    except Exception as e:
        logger.warning("Failed to retrieve payment page: %s", e)
        payment_page = None

    # 3) Resolve product_page
    product_page = None
    slug = product_code or type_to_slug(payment_type)
    if not product_page and slug:
        product_page = _get_product_page_by_slug(slug)
    if not product_page and payment_page:
        # из relation
        try:
            rel = payment_page.get("properties", {}).get("Products", {}).get("relation", [])
            if rel:
                rid = rel[0].get("id")
                if rid:
                    product_page = _client.pages.retrieve(rid)
        except Exception:
            pass
    if not product_page and payment_page:
        # из Type
        try:
            tslug = type_to_slug(_get_payment_type_value(payment_page) or "")
            if tslug:
                product_page = _get_product_page_by_slug(tslug)
        except Exception:
            pass

    # 4) Ensure Products relation and fast fields
    product_name = None
    expires_iso = None
    if product_page:
        _set_payment_products_relation(notion_payment_id, product_page["id"])
        try:
            product_name = product_page["properties"]["Name"]["title"][0]["plain_text"]
        except Exception:
            product_name = None

        paid_at = datetime.now(timezone.utc)
        access_days = product_page["properties"].get("Access days", {}).get("number")
        if access_days:
            expires_iso = (paid_at + timedelta(days=int(access_days))).isoformat()
    _set_payment_fast_fields(notion_payment_id, product_name=product_name, expires_at_iso=expires_iso)

    # 5) Invalidate cache (so user sees product instantly)
    try:
        invalidate_user_products_cache(user_telegram_id)
    except Exception:
        pass

    # 6) Create Purchase (optional, if Purchases DB configured and product resolved)
    if not _safe_id(NOTION_PURCHASES_DB_ID) or not product_page:
        return

    try:
        user_page_id = _get_user_page_by_tg(user_telegram_id)

        paid_at = datetime.now(timezone.utc)
        access_days = product_page["properties"].get("Access days", {}).get("number")
        expires_at = (paid_at + timedelta(days=int(access_days))) if access_days else None

        purchase_props = {
            "Name": {"title": [{"text": {"content": f"Purchase {(product_name or 'product')} {user_telegram_id}"}}]},
            "Status": {"select": {"name": "paid"}},
            "Paid at": {"date": {"start": paid_at.isoformat()}},
            "Product": {"relation": [{"id": product_page["id"]}]},
        }
        if user_page_id:
            purchase_props["User"] = {"relation": [{"id": user_page_id}]}
        if expires_at:
            purchase_props["Expires at"] = {"date": {"start": expires_at.isoformat()}}

        purchase_page = _client.pages.create(parent={"database_id": NOTION_PURCHASES_DB_ID}, properties=purchase_props)

        # Свяжем оба конца, если свойства есть
        try:
            _client.pages.update(page_id=notion_payment_id, properties={
                "Linked Purchase": {"relation": [{"id": purchase_page["id"]}]}
            })
        except Exception:
            pass
        try:
            _client.pages.update(page_id=purchase_page["id"], properties={
                "Payment": {"relation": [{"id": notion_payment_id}]}
            })
        except Exception:
            pass

    except Exception as e:
        logger.error("Failed to create Purchase and link: %s", e)
