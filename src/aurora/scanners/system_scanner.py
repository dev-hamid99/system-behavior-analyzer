from __future__ import annotations

import psutil

from aurora.domain.models import ScanIssue, ScanResult, SystemMetrics
from aurora.domain.risk import RiskLevel
from aurora.scanners.base import Scanner


class SystemScanner(Scanner):
    name = "system"

    def scan(self) -> ScanResult:
        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        net = psutil.net_io_counters()
        metrics = SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            ram_percent=vm.percent,
            disk_percent=du.percent,
            net_sent_mb=round(net.bytes_sent / (1024 * 1024), 2),
            net_recv_mb=round(net.bytes_recv / (1024 * 1024), 2),
        )
        issues: list[ScanIssue] = []
        if metrics.cpu_percent > 90:
            issues.append(
                ScanIssue(
                    code="cpu_high",
                    title="High CPU load",
                    details="CPU utilization is above 90%.",
                    risk=RiskLevel.HIGH,
                    category="cpu",
                )
            )
        if metrics.ram_percent > 85:
            issues.append(
                ScanIssue(
                    code="ram_high",
                    title="High memory usage",
                    details="RAM utilization is above 85%.",
                    risk=RiskLevel.MEDIUM,
                    category="memory",
                )
            )
        if metrics.disk_percent > 90:
            issues.append(
                ScanIssue(
                    code="disk_high",
                    title="Low free disk space",
                    details="Disk utilization is above 90%.",
                    risk=RiskLevel.MEDIUM,
                    category="storage",
                )
            )
        return ScanResult(metrics=metrics, issues=issues)
