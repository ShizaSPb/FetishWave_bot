
import os
import asyncio
from typing import Any, Dict, List, Optional

try:
    from notion_client import Client
except Exception as e:  # pragma: no cover
    Client = None  # type: ignore

from bot.services.cache import TTLCache

# Notion property names
PROP_CODE = "Code"
PROP_ACTIVE = "Active"
PROP_ORDER = "Order"
PROP_CURRENCY = "Currency"
PROP_BTN_RU = "Button RU"
PROP_BTN_EN = "Button EN"
PROP_DETAILS_SLUG = "Details Slug"
PROP_RATE_PER_EUR = "Rate per 1 EUR"
PROP_ROUND_TO = "Round to"

_cache = TTLCache(ttl_seconds=300)
_all_cache_key = "payment_methods:all"

def _get_client() -> Client:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN is not set")
    return Client(auth=token)

def _rich_text_to_str(rt: List[Dict[str, Any]]) -> str:
    parts = []
    for r in rt or []:
        t = r.get("plain_text") or ""
        parts.append(t)
    return "".join(parts).strip()

def _page_to_item(page: Dict[str, Any]) -> Dict[str, Any]:
    props = page.get("properties", {})
    code = _rich_text_to_str(props.get(PROP_CODE, {}).get("rich_text", []))
    active = props.get(PROP_ACTIVE, {}).get("checkbox", False)
    order = props.get(PROP_ORDER, {}).get("number", 0) or 0
    currency = props.get(PROP_CURRENCY, {}).get("select", {}).get("name") or ""
    btn_ru = _rich_text_to_str(props.get(PROP_BTN_RU, {}).get("rich_text", []))
    btn_en = _rich_text_to_str(props.get(PROP_BTN_EN, {}).get("rich_text", []))
    details_slug = _rich_text_to_str(props.get(PROP_DETAILS_SLUG, {}).get("rich_text", []))
    rate = props.get(PROP_RATE_PER_EUR, {}).get("number", None)
    round_to = props.get(PROP_ROUND_TO, {}).get("number", None)

    return {
        "code": code,
        "active": bool(active),
        "order": order,
        "currency": currency,
        "button_ru": btn_ru,
        "button_en": btn_en,
        "details_slug": details_slug,
        "rate_per_eur": float(rate) if rate is not None else None,
        "round_to": float(round_to) if round_to is not None else None,
        "id": page.get("id"),
        "last_edited_time": page.get("last_edited_time"),
    }

def _fetch_all_sync(db_id: str) -> List[Dict[str, Any]]:
    client = _get_client()
    results: List[Dict[str, Any]] = []
    cursor = None
    while True:
        resp = client.databases.query(
            **({"database_id": db_id, "start_cursor": cursor} if cursor else {"database_id": db_id}),
            filter={
                "and": [
                    {
                        "property": PROP_ACTIVE,
                        "checkbox": {"equals": True}
                    }
                ]
            },
            sorts=[{"property": PROP_ORDER, "direction": "ascending"}]
        )
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return [_page_to_item(p) for p in results]

async def preload_all(db_id: Optional[str] = None) -> int:
    db_id = db_id or os.getenv("NOTION_PAYMENT_METHODS_DB_ID", "")
    if not db_id:
        raise RuntimeError("NOTION_PAYMENT_METHODS_DB_ID is not set")
    items = await asyncio.to_thread(_fetch_all_sync, db_id)
    index: Dict[str, Dict[str, Any]] = {}
    for it in items:
        if not it.get("code"):
            # skip invalid row
            continue
        index[it["code"]] = it
    _cache.set(_all_cache_key, index)
    return len(index)

def _get_index() -> Dict[str, Dict[str, Any]]:
    idx = _cache.get(_all_cache_key)
    return idx or {}

async def reload() -> int:
    _cache.clear()
    return await preload_all()

async def get_all() -> List[Dict[str, Any]]:
    idx = _get_index()
    if not idx:
        await preload_all()
        idx = _get_index()
    # return as sorted list by 'order'
    return sorted(idx.values(), key=lambda x: x.get("order", 0))

async def get(code: str) -> Optional[Dict[str, Any]]:
    idx = _get_index()
    if not idx:
        await preload_all()
        idx = _get_index()
    return idx.get(code)

def compute_amount_eur_to_method(price_eur: float, method: Dict[str, Any]) -> float:
    rate = method.get("rate_per_eur")
    if rate is None:
        raise ValueError(f"Payment method {method.get('code')} has no 'Rate per 1 EUR' set")
    amount = price_eur * float(rate)
    round_to = method.get("round_to")
    if round_to and round_to > 0:
        # round to nearest multiple of round_to
        k = int(round(amount / round_to))
        amount = k * round_to
    return float(amount)

def cache_info() -> Dict[str, Any]:
    return _cache.info()
