import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from notion_client import Client
from config import NOTION_TOKEN

# New DBs that must be defined in config/.env
try:
    from config import NOTION_PRODUCTS_DB_ID, NOTION_PAYMENTS_DB_ID, NOTION_PURCHASES_DB_ID  # type: ignore
except Exception:
    # placeholders (will raise later if used)
    NOTION_PRODUCTS_DB_ID = None
    NOTION_PAYMENTS_DB_ID = None
    NOTION_PURCHASES_DB_ID = None

logger = logging.getLogger(__name__)
notion = Client(auth=NOTION_TOKEN)


# ---------- USERS ----------
async def get_user_page_id_by_telegram(telegram_id: int) -> Optional[str]:
    """Return Notion page id for user by Telegram ID."""
    if not telegram_id:
        return None
    resp = notion.databases.query(
        database_id=getattr(__import__('config'), 'NOTION_USERS_DB_ID'),
        filter={
            "property": "Telegram ID",
            "number": {"equals": int(telegram_id)}
        },
        page_size=1
    )
    results = resp.get("results", [])
    return results[0]["id"] if results else None


async def get_user_brief_by_page_id(page_id: str) -> Dict[str, Any]:
    pg = notion.pages.retrieve(page_id=page_id)
    props = pg.get("properties", {})
    username = ""
    try:
        rt = props["Username"]["rich_text"]
        if rt:
            username = rt[0]["plain_text"]
    except Exception:
        pass
    tid = None
    try:
        tid = props["Telegram ID"]["number"]
    except Exception:
        pass
    return {"page_id": page_id, "telegram_id": tid, "username": username}


# ---------- PRODUCTS ----------
def _str(p): return str(p) if p is not None else ""

async def get_product_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    if not NOTION_PRODUCTS_DB_ID:
        raise RuntimeError("NOTION_PRODUCTS_DB_ID is not configured")
    resp = notion.databases.query(
        database_id=NOTION_PRODUCTS_DB_ID,
        filter={
            "property": "Slug/Code",
            "rich_text": {"equals": slug}
        },
        page_size=1
    )
    results = resp.get("results", [])
    if not results:
        return None
    page = results[0]
    props = page["properties"]
    def _get_select_name(key):
        try:
            return props[key]["select"]["name"]
        except Exception:
            return None

    access_mode = (_get_select_name("Access mode") or "").lower()
    access_days = None
    try:
        access_days = props["Access days"]["number"]
    except Exception:
        pass

    resource_ref = None
    try:
        rt = props["Resource ref"]["rich_text"]
        if rt:
            resource_ref = rt[0]["plain_text"]
    except Exception:
        pass

    name = ""
    try:
        t = props["Name"]["title"]
        if t:
            name = t[0]["plain_text"]
    except Exception:
        pass

    active = True
    try:
        active = props["Active"]["checkbox"]
    except Exception:
        pass

    return {
        "id": page["id"],
        "page_id": page["id"],
        "slug": slug,
        "name": name,
        "access_mode": access_mode,
        "access_days": access_days,
        "resource_ref": resource_ref,
        "active": active
    }


# ---------- PAYMENTS ----------
async def create_payment(
    user_page_id: Optional[str],
    product_page_id: Optional[str],
    telegram_id: int,
    proof_tg_file_id: str,
    status: str,
    amount: Optional[str],
    currency: Optional[str],
    idempotency_token: str,
    payment_type: str,
) -> Dict[str, Any]:
    if not NOTION_PAYMENTS_DB_ID:
        raise RuntimeError("NOTION_PAYMENTS_DB_ID is not configured")
    if not user_page_id:
        raise RuntimeError("User page not found in Notion for this Telegram ID")

    props = {
        "User": {"relation": [{"id": user_page_id}]},
        "Status": {"select": {"name": status}},
        "Idempotency": {"rich_text": [{"text": {"content": idempotency_token}}]},
        "Telegram ID": {"number": int(telegram_id)},
        "Proof TG file_id": {"rich_text": [{"text": {"content": proof_tg_file_id}}]},
        "Type": {"rich_text": [{"text": {"content": payment_type}}]},
    }
    if amount:
        props["Amount"] = {"rich_text": [{"text": {"content": str(amount)}}]}
    if currency:
        props["Currency"] = {"rich_text": [{"text": {"content": str(currency)}}]}
    if product_page_id:
        props["Product"] = {"relation": [{"id": product_page_id}]}

    page = notion.pages.create(parent={"database_id": NOTION_PAYMENTS_DB_ID}, properties=props)
    return {"id": page["id"]}


async def get_payment(payment_page_id: str) -> Optional[Dict[str, Any]]:
    if not payment_page_id:
        return None
    page = notion.pages.retrieve(page_id=payment_page_id)
    props = page["properties"]

    # Parse
    status = None
    try:
        status = props["Status"]["select"]["name"]
    except Exception:
        pass
    idempotency = None
    try:
        rt = props["Idempotency"]["rich_text"]
        if rt:
            idempotency = rt[0]["plain_text"]
    except Exception:
        pass

    # Get user brief
    user_page_id = None
    try:
        rel = props["User"]["relation"]
        if rel:
            user_page_id = rel[0]["id"]
    except Exception:
        pass
    user = await get_user_brief_by_page_id(user_page_id) if user_page_id else {}

    # Get product brief
    product = {}
    try:
        rel = props["Product"]["relation"]
        product_page_id = rel[0]["id"] if rel else None
        if product_page_id:
            product_page = notion.pages.retrieve(page_id=product_page_id)
            p_props = product_page["properties"]
            name = ""
            try:
                t = p_props["Name"]["title"]
                if t:
                    name = t[0]["plain_text"]
            except Exception:
                pass
            slug = None
            try:
                r = p_props["Slug/Code"]["rich_text"]
                if r:
                    slug = r[0]["plain_text"]
            except Exception:
                pass
            access_mode = None
            try:
                access_mode = p_props["Access mode"]["select"]["name"]
            except Exception:
                pass
            access_days = None
            try:
                access_days = p_props["Access days"]["number"]
            except Exception:
                pass
            resource_ref = None
            try:
                r = p_props["Resource ref"]["rich_text"]
                if r:
                    resource_ref = r[0]["plain_text"]
            except Exception:
                pass
            product = {
                "page_id": product_page_id,
                "name": name,
                "slug": slug,
                "access_mode": access_mode,
                "access_days": access_days,
                "resource_ref": resource_ref,
            }
    except Exception:
        pass

    return {
        "id": page["id"],
        "status": status,
        "idempotency": idempotency,
        "user": user,
        "product": product,
    }


async def set_payment_status(payment_page_id: str, status: str, admin: Optional[str], processed_at: Optional[datetime], linked_purchase_id: Optional[str]):
    props = {"Status": {"select": {"name": status}}}
    if admin:
        props["Admin"] = {"rich_text": [{"text": {"content": str(admin)}}]}
    if processed_at:
        props["Processed at"] = {"date": {"start": processed_at.isoformat()}}
    if linked_purchase_id:
        props["Linked Purchase"] = {"relation": [{"id": linked_purchase_id}]}
    notion.pages.update(page_id=payment_page_id, properties=props)


# ---------- PURCHASES ----------
async def create_or_update_purchase(
    user_page_id: str,
    product_page_id: str,
    access_days: Optional[int],
    payment_page_id: Optional[str],
) -> Dict[str, Any]:
    if not NOTION_PURCHASES_DB_ID:
        raise RuntimeError("NOTION_PURCHASES_DB_ID is not configured")
    # Try to find active existing purchase
    existing = None
    q = notion.databases.query(
        database_id=NOTION_PURCHASES_DB_ID,
        filter={
            "and": [
                {"property": "User", "relation": {"contains": user_page_id}},
                {"property": "Product", "relation": {"contains": product_page_id}},
                {"property": "Status", "select": {"equals": "paid"}},
            ]
        },
        page_size=1
    )
    results = q.get("results", [])
    if results:
        existing = results[0]

    now = datetime.utcnow()
    expires_at = None
    if isinstance(access_days, (int, float)) and access_days:
        expires_at = (now + timedelta(days=int(access_days))).isoformat()

    if existing:
        # Optionally extend expiration if set
        props = {}
        if expires_at:
            props["Expires at"] = {"date": {"start": expires_at}}
        page_id = existing["id"]
        if props:
            notion.pages.update(page_id=page_id, properties=props)
        # ensure status paid
        notion.pages.update(page_id=page_id, properties={"Status": {"select": {"name": "paid"}}})
        return {"id": page_id, "license_token": None}

    # else create new
    props = {
        "User": {"relation": [{"id": user_page_id}]},
        "Product": {"relation": [{"id": product_page_id}]},
        "Status": {"select": {"name": "paid"}},
        "Paid at": {"date": {"start": now.isoformat()}},
    }
    if expires_at:
        props["Expires at"] = {"date": {"start": expires_at}}
    if payment_page_id:
        props["Payment"] = {"relation": [{"id": payment_page_id}]}
    pg = notion.pages.create(parent={"database_id": NOTION_PURCHASES_DB_ID}, properties=props)
    return {"id": pg["id"], "license_token": None}
