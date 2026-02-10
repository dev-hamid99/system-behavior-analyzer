from __future__ import annotations

from aurora.domain.models import ScanResult
from aurora.scanners.system_scanner import SystemScanner


class DriversScanner(SystemScanner):
    name = "drivers"

    def scan(self) -> ScanResult:
        return super().scan()
