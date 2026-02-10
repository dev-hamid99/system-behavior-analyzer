from __future__ import annotations

from aurora.actions.base import Action
from aurora.core.permissions import require_user_confirmation
from aurora.domain.models import ActionPreview, ActionResult
from aurora.domain.risk import RiskLevel


class SimulatedAction(Action):
    def __init__(self, action_id: str, title: str, risk: RiskLevel, changes: list[str]) -> None:
        self.id = action_id
        self.title = title
        self._risk = risk
        self._changes = changes
        self._applied = False

    def preview(self) -> ActionPreview:
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
        return ActionResult(action_id=self.id, success=True, message=f"Applied: {self.title}")

    def rollback(self) -> ActionResult:
        if not self._applied:
            return ActionResult(action_id=self.id, success=False, message="Nothing to rollback")
        self._applied = False
        return ActionResult(action_id=self.id, success=True, message=f"Rolled back: {self.title}")
