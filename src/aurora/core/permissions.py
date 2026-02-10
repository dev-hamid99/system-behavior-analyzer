from __future__ import annotations

from aurora.core.errors import ActionSafetyError


def require_user_confirmation(confirmed: bool) -> None:
    if not confirmed:
        raise ActionSafetyError("User confirmation required before applying action.")
