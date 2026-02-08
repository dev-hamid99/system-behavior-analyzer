from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any

import psutil


@dataclass(frozen=True)
class SystemMetrics:
    ts_utc: str
    cpu_percent: float
    mem_percent: float
    mem_used_mb: float
    disk_percent: float
    net_sent_kb_s: float
    net_recv_kb_s: float


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def collect_once(prev_net: Any | None, interval_sec: float) -> tuple[SystemMetrics, Any]:
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    net_now = psutil.net_io_counters()
    if prev_net is None:
        sent_kb_s = 0.0
        recv_kb_s = 0.0
    else:
        sent_kb_s = (net_now.bytes_sent - prev_net.bytes_sent) / 1024.0 / max(interval_sec, 1e-6)
        recv_kb_s = (net_now.bytes_recv - prev_net.bytes_recv) / 1024.0 / max(interval_sec, 1e-6)

    metrics = SystemMetrics(
        ts_utc=_utc_now_iso(),
        cpu_percent=float(cpu),
        mem_percent=float(mem.percent),
        mem_used_mb=float(mem.used) / (1024.0 * 1024.0),
        disk_percent=float(disk.percent),
        net_sent_kb_s=float(sent_kb_s),
        net_recv_kb_s=float(recv_kb_s),
    )
    return metrics, net_now


def metrics_to_dict(m: SystemMetrics) -> dict:
    return asdict(m)
