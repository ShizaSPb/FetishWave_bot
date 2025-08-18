# bot/scripts/backfill_payment_fast_fields.py
"""
Одноразовый скрипт: заполнить/создать в Payments поля Product Name / Expires at и проставить их для оплаченных платежей.
Запуск:  python -m bot.scripts.backfill_payment_fast_fields
"""

import logging
from datetime import datetime, timedelta, timezone

from notion_client import Client
from config import NOTION_TOKEN, NOTION_PRODUCTS_DB_ID, NOTION_PAYMENTS_DB_ID
from bot.utils.product_codes import type_to_slug

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

client = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

PRODUCT_NAME_PROP = "Product Name"
EXPIRES_AT_PROP = "Expires at"

def _safe_id(v):
    return v and isinstance(v, str)

def _iso_to_dt(s: str):
    if not s:
        return None
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        return datetime.fromisoformat(s)
    except Exception:
        return None

def _ensure_fast_fields_exist():
    try:
        db = client.databases.retrieve(NOTION_PAYMENTS_DB_ID)
        props = db.get("properties", {}) or {}
        need_update = {}
        if PRODUCT_NAME_PROP not in props:
            need_update[PRODUCT_NAME_PROP] = {"rich_text": {}}
        if EXPIRES_AT_PROP not in props:
            need_update[EXPIRES_AT_PROP] = {"date": {}}
        if need_update:
            client.databases.update(NOTION_PAYMENTS_DB_ID, properties=need_update)
            log.info("Added missing properties to Payments DB: %s", ", ".join(need_update.keys()))
    except Exception as e:
        log.warning("Failed to ensure fast fields exist: %s", e)

def _get_product_page_by_slug(slug: str):
    if not _safe_id(NOTION_PRODUCTS_DB_ID) or not slug or client is None:
        return None
    try:
        r = client.databases.query(
            database_id=NOTION_PRODUCTS_DB_ID,
            filter={"property": "Slug/Code", "rich_text": {"equals": slug}}
        )
        if r["results"]:
            return r["results"][0]
    except Exception as e:
        log.warning("Products query failed for slug %s: %s", slug, e)
    return None

def _set_payment_fast_fields(payment_page_id: str, *, product_name: str|None, expires_at_iso: str|None):
    props = {}
    if product_name:
        props[PRODUCT_NAME_PROP] = {"rich_text": [{"text": {"content": product_name}}]}
    if expires_at_iso:
        props[EXPIRES_AT_PROP] = {"date": {"start": expires_at_iso}}
    if not props:
        return
    client.pages.update(page_id=payment_page_id, properties=props)

def main():
    if not _safe_id(NOTION_PAYMENTS_DB_ID) or client is None:
        print("Notion not configured")
        return

    _ensure_fast_fields_exist()

    # Берём только paid-платежи, где Product Name пуст
    res = client.databases.query(
        database_id=NOTION_PAYMENTS_DB_ID,
        filter={"and": [
            {"property": "Status", "select": {"equals": "paid"}},
            {"property": PRODUCT_NAME_PROP, "rich_text": {"is_empty": True}},
        ]},
        page_size=100,
    )
    print(f"Found {len(res.get('results', []))} payments to backfill")

    for row in res.get("results", []):
        props = row.get("properties", {})
        pid = row["id"]

        # product_page: из relation Products или по slug из Type
        product_page = None
        rel = props.get("Products", {}).get("relation", [])
        if rel:
            rid = rel[0].get("id")
            if rid:
                product_page = client.pages.retrieve(rid)
        if not product_page:
            type_val = None
            t = props.get("Type")
            if isinstance(t, dict):
                if t.get("select"):
                    type_val = t["select"]["name"]
                elif t.get("rich_text"):
                    type_val = "".join([s.get("plain_text") or s.get("text", {}).get("content", "") for s in t["rich_text"]]).strip()
            slug = type_to_slug(type_val or "")
            if slug:
                product_page = _get_product_page_by_slug(slug)

        product_name = None
        expires_iso = None
        if product_page:
            try:
                product_name = product_page["properties"]["Name"]["title"][0]["plain_text"]
            except Exception:
                pass
            access_days = product_page["properties"].get("Access days", {}).get("number")
            paid_at = None
            try:
                paid_at = props.get("Processed at", {}).get("date", {}).get("start")
                paid_at = _iso_to_dt(paid_at)
                if paid_at and paid_at.tzinfo is None:
                    paid_at = paid_at.replace(tzinfo=timezone.utc)
            except Exception:
                paid_at = None
            if access_days and paid_at:
                expires_iso = (paid_at + timedelta(days=int(access_days))).isoformat()

        _set_payment_fast_fields(pid, product_name=product_name, expires_at_iso=expires_iso)
        print(f"Updated {pid}: name={product_name}, expires={expires_iso}")

if __name__ == "__main__":
    main()
