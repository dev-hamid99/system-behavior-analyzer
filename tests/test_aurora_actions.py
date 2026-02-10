from __future__ import annotations

import pytest

from aurora.actions.builtin.cleanup_temp import CleanupTempAction
from aurora.core.errors import ActionSafetyError


def test_action_preview_apply_rollback() -> None:
    action = CleanupTempAction()
    preview = action.preview()
    assert preview.action_id == "cleanup_temp"

    with pytest.raises(ActionSafetyError):
        action.apply(confirmed=False)

    applied = action.apply(confirmed=True)
    assert applied.success

    rolled_back = action.rollback()
    assert rolled_back.success
