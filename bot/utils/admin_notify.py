# -*- coding: utf-8 -*-
"""
Безопасные уведомления админам.
Использование в payments.py:
    from bot.utils.admin_notify import notify_admins_file, notify_admins_message
    await notify_admins_file(context, file_id, is_document=True, caption="...", parse_mode="HTML")
"""
import os
from typing import List, Optional

def _parse_env_admin_ids(s: Optional[str]) -> List[int]:
    ids = []
    if s and s.strip():
        for part in s.split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
    return ids

def get_admin_ids() -> List[int]:
    # 1) ENV приоритетнее
    ids = _parse_env_admin_ids(os.getenv("ADMIN_IDS", ""))
    if ids:
        return ids
    # 2) config.ADMIN_IDS
    try:
        from config import ADMIN_IDS as CFG_IDS  # type: ignore
        if CFG_IDS:
            return list(CFG_IDS)
    except Exception:
        pass
    # 3) config.ADMIN_CHAT_ID (совместимость)
    try:
        from config import ADMIN_CHAT_ID as CHAT_ID  # type: ignore
        if CHAT_ID:
            return [int(CHAT_ID)]
    except Exception:
        pass
    return []

async def notify_admins_message(context, text: str, **kwargs):
    ids = get_admin_ids()
    if not ids:
        raise RuntimeError("No admin ids configured (ADMIN_IDS or ADMIN_CHAT_ID).")
    for aid in ids:
        await context.bot.send_message(chat_id=aid, text=text, **kwargs)

async def notify_admins_file(context, file_id: str, is_document: bool = True, **kwargs):
    ids = get_admin_ids()
    if not ids:
        raise RuntimeError("No admin ids configured (ADMIN_IDS or ADMIN_CHAT_ID).")
    for aid in ids:
        if is_document:
            await context.bot.send_document(chat_id=aid, document=file_id, **kwargs)
        else:
            await context.bot.send_photo(chat_id=aid, photo=file_id, **kwargs)
