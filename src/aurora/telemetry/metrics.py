from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InternalMetric:
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
