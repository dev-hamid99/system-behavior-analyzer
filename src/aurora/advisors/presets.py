from __future__ import annotations

from aurora.domain.profiles import BATTERY_PROFILE, GAMING_PROFILE, WORK_PROFILE

SAFE_PRESETS = {
    "gaming": GAMING_PROFILE,
    "work": WORK_PROFILE,
    "battery": BATTERY_PROFILE,
}
