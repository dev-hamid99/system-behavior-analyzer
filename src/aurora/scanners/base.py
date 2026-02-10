from __future__ import annotations

from abc import ABC, abstractmethod

from aurora.domain.models import ScanResult


class Scanner(ABC):
    name: str

    @abstractmethod
    def scan(self) -> ScanResult:
        raise NotImplementedError
