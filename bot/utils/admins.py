
import os

def is_admin(user_id: int) -> bool:
    raw = os.getenv("ADMIN_IDS", "") or ""
    ids = [x.strip() for x in raw.split(",") if x.strip()]
    return str(user_id) in ids
