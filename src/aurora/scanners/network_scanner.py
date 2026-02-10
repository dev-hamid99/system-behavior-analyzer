from __future__ import annotations

from aurora.domain.models import ScanResult
from aurora.scanners.system_scanner import SystemScanner


class NetworkScanner(SystemScanner):
    name = "network"

    def scan(self) -> ScanResult:
        return super().scan()
