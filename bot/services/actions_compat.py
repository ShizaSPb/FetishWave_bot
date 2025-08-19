# bot/services/actions_compat.py
from __future__ import annotations
from typing import Any

def patch_log_action_positional() -> None:
    import bot.services.actions as actions  # type: ignore
    if getattr(actions, "_pos_compat_installed", False):
        return

    orig = actions.log_action  # type: ignore[attr-defined]

    def _wrapped(event: str, *args: Any, **fields: Any) -> None:
        if args:
            first = args[0]
            if isinstance(first, int) and "user_id" not in fields:
                fields["user_id"] = first
            if len(args) >= 2:
                second = args[1]
                if isinstance(second, dict):
                    for k, v in second.items():
                        fields.setdefault(k, v)
                else:
                    fields.setdefault("metadata", second)
        return orig(event, **fields)  # type: ignore[misc]

    actions.log_action = _wrapped  # type: ignore[assignment]
    actions._pos_compat_installed = True  # type: ignore[attr-defined]
