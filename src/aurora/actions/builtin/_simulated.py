from __future__ import annotations

import logging

from aurora.actions.base import Action
from aurora.core.permissions import require_user_confirmation
from aurora.domain.models import ActionPreview, ActionResult
from aurora.domain.risk import RiskLevel
from aurora.storage.repositories import sqlite_repo

log = logging.getLogger(__name__)


class SimulatedAction(Action):
    def __init__(self, action_id: str, title: str, risk: RiskLevel, changes: list[str]) -> None:
        self.id = action_id
        self.title = title
        self._risk = risk
        self._changes = changes
        self._applied = False

    def _audit(self, event_type: str, message: str) -> None:
        try:
            sqlite_repo().add_audit(event_type, message)
        except Exception as exc:  # pragma: no cover - defensive
            log.exception("audit-write-failed action=%s error=%r", self.id, exc)

    def preview(self) -> ActionPreview:
        self._audit("action.preview", f"preview requested for {self.id}")
        return ActionPreview(
            action_id=self.id,
            title=self.title,
            changes=self._changes,
            risk=self._risk,
            rollback_hint="Use rollback to restore previously captured state.",
        )

    def apply(self, confirmed: bool = False) -> ActionResult:
        require_user_confirmation(confirmed)
        self._applied = True
        self._audit("action.apply", f"applied action {self.id}")
        return ActionResult(action_id=self.id, success=True, message=f"Applied: {self.title}")

    def rollback(self) -> ActionResult:
        if not self._applied:
            result = ActionResult(action_id=self.id, success=False, message="Nothing to rollback")
            self._audit("action.rollback", f"rollback skipped for {self.id}: not applied")
            return result
        self._applied = False
        self._audit("action.rollback", f"rolled back action {self.id}")
        return ActionResult(action_id=self.id, success=True, message=f"Rolled back: {self.title}")
