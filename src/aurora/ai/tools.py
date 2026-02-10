from __future__ import annotations

from typing import TypedDict

from aurora.advisors.rules_engine import RulesEngine
from aurora.domain.models import ScanIssue, SystemMetrics
from aurora.scanners.system_scanner import SystemScanner


class QuickScanPayload(TypedDict):
    metrics: SystemMetrics
    issues: list[ScanIssue]
    recommendations: list[str]


def run_quick_scan() -> QuickScanPayload:
    scanner = SystemScanner()
    result = scanner.scan()
    recs = RulesEngine().recommend(result)
    return {
        "metrics": result.metrics,
        "issues": result.issues,
        "recommendations": recs,
    }
