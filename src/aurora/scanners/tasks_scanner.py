from __future__ import annotations

from aurora.domain.models import ScanResult
from aurora.scanners.system_scanner import SystemScanner


class TasksScanner(SystemScanner):
    name = "tasks"

    def scan(self) -> ScanResult:
        return super().scan()
