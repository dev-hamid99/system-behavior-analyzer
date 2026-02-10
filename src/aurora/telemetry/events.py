from __future__ import annotations

from aurora.domain.audit import AuditEvent


def ui_event(name: str, message: str) -> AuditEvent:
    return AuditEvent(event_type=f"ui.{name}", message=message)
