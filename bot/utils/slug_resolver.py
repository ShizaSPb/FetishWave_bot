# -*- coding: utf-8 -*-
"""
Helper to resolve product slug for payments.
Usage in payments.py:
    from bot.utils.slug_resolver import get_payment_slug
    payment_slug = get_payment_slug(context)
"""
import os
import logging
log = logging.getLogger(__name__)

def get_payment_slug(context, env_var="DEFAULT_PRODUCT_SLUG"):
    # 1) try user selection saved by /products
    try:
        slug = context.user_data.get("current_payment_type")
    except Exception:
        slug = None
    # 2) fallback to env DEFAULT_PRODUCT_SLUG
    if not slug:
        slug = os.getenv(env_var)
    # 3) normalize / log
    if slug:
        return slug.strip()
    log.error("Product slug is missing. Set via /products or set %s in .env", env_var)
    return None
