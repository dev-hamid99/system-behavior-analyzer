from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import psutil
from PySide6.QtCore import QThread, Signal


@dataclass(frozen=True)
class SystemSample:
    ts: float
    cpu: float
    ram: float
    disk: float
    net_kbps: float


class SystemWorker(QThread):
    """
    Background sampler. Emits SystemSample on a fixed interval.

    - Uses psutil for CPU/RAM/Disk/Net.
    - Runs in a thread so UI stays smooth.
    """
    sample = Signal(object)   # emits SystemSample
    live = Signal(bool)       # emits True on start, False on stop
    error = Signal(str)

    def __init__(self, interval_s: float = 1.0, disk_path: str = "C:\\") -> None:
        super().__init__()
        self.interval_s = float(max(0.2, interval_s))
        self.disk_path = disk_path
        self._running = True

        self._last_net_bytes: Optional[int] = None
        self._last_ts: Optional[float] = None

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        try:
            self.live.emit(True)

            # Prime network counters
            nc = psutil.net_io_counters()
            self._last_net_bytes = int(nc.bytes_sent + nc.bytes_recv)
            self._last_ts = time.time()

            # Prime CPU to avoid first weird reading
            psutil.cpu_percent(interval=None)

            while self._running:
                t0 = time.time()

                cpu = float(psutil.cpu_percent(interval=None))
                ram = float(psutil.virtual_memory().percent)

                # Disk %
                try:
                    disk = float(psutil.disk_usage(self.disk_path).percent)
                except Exception:
                    disk = float("nan")

                # Net KB/s (delta bytes / delta time)
                nc2 = psutil.net_io_counters()
                now_bytes = int(nc2.bytes_sent + nc2.bytes_recv)
                now_ts = time.time()

                dt = max(1e-6, now_ts - (self._last_ts or now_ts))
                dbytes = now_bytes - (self._last_net_bytes or now_bytes)
                net_kbps = (dbytes / dt) / 1024.0

                self._last_net_bytes = now_bytes
                self._last_ts = now_ts

                self.sample.emit(SystemSample(
                    ts=now_ts,
                    cpu=cpu,
                    ram=ram,
                    disk=disk,
                    net_kbps=float(net_kbps),
                ))

                # Keep interval stable
                elapsed = time.time() - t0
                sleep_s = max(0.0, self.interval_s - elapsed)
                time.sleep(sleep_s)

        except Exception as e:
            self.error.emit(f"{type(e).__name__}: {e}")
        finally:
            self.live.emit(False)
