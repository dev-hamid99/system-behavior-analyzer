from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from aurora.domain.risk import RiskLevel


@dataclass(frozen=True)
class SystemMetrics:
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    net_sent_mb: float
    net_recv_mb: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ScanIssue:
    code: str
    title: str
    details: str
    risk: RiskLevel
    category: str


@dataclass(frozen=True)
class ScanResult:
    metrics: SystemMetrics
    issues: list[ScanIssue]


@dataclass(frozen=True)
class ActionPreview:
    action_id: str
    title: str
    changes: list[str]
    risk: RiskLevel
    rollback_hint: str


@dataclass(frozen=True)
class ActionResult:
    action_id: str
    success: bool
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
