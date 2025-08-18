# bot/utils/product_codes.py
"""
Mapping payment 'type' values to Notion Products slug.
"""

import re

# Explicit aliases if some Type values don't match simple rules
EXPLICIT_ALIASES = {
    # example: "webinar_femdom": "femdom_part_both",
}

def type_to_slug(value: str) -> str | None:
    """
    Convert strings like 'webinar_joi' or 'webinar_webinar_joi'
    to Notion Products slug ('joi', 'femdom_part_1', ...).

    Rules:
      - remove ALL 'webinar_' prefixes
      - special: 'femdom' -> 'femdom_part_both'
      - keep only [a-z0-9_]
    """
    if not value:
        return None

    v = value.strip().lower()

    if v in EXPLICIT_ALIASES:
        return EXPLICIT_ALIASES[v]

    while v.startswith("webinar_"):
        v = v[len("webinar_"):]

    if v == "femdom":
        v = "femdom_part_both"

    v = re.sub(r"[^a-z0-9_]+", "_", v).strip("_")
    return v or None
