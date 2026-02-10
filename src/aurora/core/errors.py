from __future__ import annotations


class AuroraError(Exception):
    """Base error for AURORA."""


class ActionSafetyError(AuroraError):
    """Raised when an unsafe action was requested without explicit consent."""
