from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PerformanceProfile:
    name: str
    description: str


GAMING_PROFILE = PerformanceProfile(
    name="gaming",
    description="Prioritize responsiveness and reduce non-essential background load.",
)
WORK_PROFILE = PerformanceProfile(
    name="work",
    description="Balanced stability profile with reduced distractions.",
)
BATTERY_PROFILE = PerformanceProfile(
    name="battery_saver",
    description="Conservative profile for lower power consumption.",
)
