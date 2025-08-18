
import os
import asyncio
from typing import Any, Dict, List, Optional

try:
    from notion_client import Client
except Exception:  # pragma: no cover
    Client = None  # type: ignore

from bot.services.cache import TTLCache

# Notion property names
PROP_SLUG = "Slug/Code"
PROP_LANGUAGE = "Language"
PROP_STATUS = "Status"   # SELECT type
PROP_SHORT = "Short"
PROP_FULL = "Full"

_cache = TTLCache(ttl_seconds=300)
_all_cache_key = "descriptions:all"

def _get_client() -> Client:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN is not set")
    return Client(auth=token)

def _rich_text_to_str(rt: List[Dict[str, Any]]) -> str:
    parts = []
    for r in rt or []:
        parts.append(r.get("plain_text") or "")
    return "".join(parts).strip()

def _page_to_item(page: Dict[str, Any]) -> Dict[str, Any]:
    props = page.get("properties", {})
    slug = _rich_text_to_str(props.get(PROP_SLUG, {}).get("rich_text", []))
    lang = props.get(PROP_LANGUAGE, {}).get("select", {}).get("name") or ""
    status_val = props.get(PROP_STATUS, {}).get("select", {}).get("name") or ""
    short = _rich_text_to_str(props.get(PROP_SHORT, {}).get("rich_text", []))
    full = _rich_text_to_str(props.get(PROP_FULL, {}).get("rich_text", []))
    return {
        "slug": slug,
        "language": lang,
        "status": status_val,
        "short": short,
        "full": full,
        "id": page.get("id"),
        "last_edited_time": page.get("last_edited_time"),
    }

def _fetch_all_sync(db_id: str) -> List[Dict[str, Any]]:
    client = _get_client()
    results: List[Dict[str, Any]] = []
    cursor = None
    while True:
        resp = client.databases.query(
            database_id=db_id,
            filter={
                "and": [
                    {
                        "property": "Status",
                        "select": {"equals": "Active"},
                    }
                ]
            }
        )
        results.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return [_page_to_item(p) for p in results]

async def preload_all(db_id: Optional[str] = None) -> int:
    db_id = db_id or os.getenv("NOTION_DESCRIPTIONS_DB_ID", "")
    if not db_id:
        raise RuntimeError("NOTION_DESCRIPTIONS_DB_ID is not set")
    items = await asyncio.to_thread(_fetch_all_sync, db_id)
    index = {}
    for it in items:
        key = f"{it['slug']}::{it['language']}"
        index[key] = it
    _cache.set(_all_cache_key, index)
    return len(index)

def _get_index() -> Dict[str, Dict[str, Any]]:
    return _cache.get(_all_cache_key) or {}

async def reload() -> int:
    _cache.clear()
    return await preload_all()

async def get_text(slug: str, language: str, kind: str = "full") -> Optional[str]:
    idx = _get_index()
    key = f"{slug}::{language}"
    item = idx.get(key)
    if not item:
        await preload_all()
        idx = _get_index()
        item = idx.get(key)
        if not item:
            return None
    if kind == "short":
        return item.get("short") or None
    return item.get("full") or None

def cache_info() -> Dict[str, Any]:
    return _cache.info()
