from __future__ import annotations

from aurora.actions.builtin.cleanup_temp import CleanupTempAction


class DummyStore:
    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def add_audit(self, event_type: str, message: str) -> None:
        self.events.append((event_type, message))


def test_actions_write_audit(monkeypatch) -> None:
    from aurora.actions.builtin import _simulated

    store = DummyStore()
    monkeypatch.setattr(_simulated, "sqlite_repo", lambda: store)

    action = CleanupTempAction()
    _ = action.preview()
    _ = action.apply(confirmed=True)
    _ = action.rollback()

    event_types = [event[0] for event in store.events]
    assert "action.preview" in event_types
    assert "action.apply" in event_types
    assert "action.rollback" in event_types
