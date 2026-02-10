from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PrivacySettings:
    ai_enabled: bool = True
    local_logs_only: bool = True
