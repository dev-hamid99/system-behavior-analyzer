from __future__ import annotations

from collections.abc import Iterable

from aurora.actions.base import Action


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    def register(self, action: Action) -> None:
        self._actions[action.id] = action

    def get(self, action_id: str) -> Action:
        return self._actions[action_id]

    def all(self) -> Iterable[Action]:
        return self._actions.values()
