from __future__ import annotations

from abc import ABC, abstractmethod

from aurora.domain.models import ActionPreview, ActionResult


class Action(ABC):
    id: str
    title: str

    @abstractmethod
    def preview(self) -> ActionPreview:
        raise NotImplementedError

    @abstractmethod
    def apply(self, confirmed: bool = False) -> ActionResult:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> ActionResult:
        raise NotImplementedError
