from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class Sample:
    ts: float
    cpu: float
    ram: float
    disk: float
    net_kbps: float


@dataclass(frozen=True)
class Model:
    mean: np.ndarray  # shape (4,)
    std: np.ndarray   # shape (4,)
    trained_on: int


@dataclass(frozen=True)
class Anomaly:
    ts: float
    cpu: float
    ram: float
    disk: float
    net_kbps: float
    z: Tuple[float, float, float, float]
    score: float
    reason: str


class Session:
    """
    Stores samples, trains a baseline model (mean/std), runs z-score detection.
    """

    def __init__(self) -> None:
        self.samples: List[Sample] = []
        self.model: Optional[Model] = None
        self.anomalies: List[Anomaly] = []

    def add(self, s: Sample) -> None:
        self.samples.append(s)

    def count(self) -> int:
        return len(self.samples)

    def can_train(self, min_samples: int = 60) -> bool:
        return len(self.samples) >= min_samples

    def train(self, window: Optional[int] = None) -> Model:
        """
        Train baseline on all samples or last `window` samples.
        """
        if not self.samples:
            raise ValueError("No samples to train on.")

        data = self.samples[-window:] if window and window > 0 else self.samples
        X = np.array([[s.cpu, s.ram, s.disk, s.net_kbps] for s in data], dtype=float)

        mean = X.mean(axis=0)
        std = X.std(axis=0)

        # avoid division by zero
        std = np.where(std < 1e-6, 1.0, std)

        m = Model(mean=mean, std=std, trained_on=len(data))
        self.model = m
        return m

    def can_detect(self) -> bool:
        return self.model is not None and len(self.samples) > 0

    def detect_last(self, z_thresh: float = 3.0) -> Optional[Anomaly]:
        """
        Detect anomaly on last sample using z-score.
        Returns Anomaly or None.
        """
        if not self.can_detect():
            return None

        s = self.samples[-1]
        x = np.array([s.cpu, s.ram, s.disk, s.net_kbps], dtype=float)

        mean = self.model.mean
        std = self.model.std

        z = (x - mean) / std
        score = float(np.max(np.abs(z)))

        # Identify reason
        labels = ["CPU", "RAM", "Disk", "Net"]
        idx = int(np.argmax(np.abs(z)))
        reason = f"{labels[idx]} z={z[idx]:.2f}"

        if score >= z_thresh:
            a = Anomaly(
                ts=s.ts,
                cpu=s.cpu,
                ram=s.ram,
                disk=s.disk,
                net_kbps=s.net_kbps,
                z=(float(z[0]), float(z[1]), float(z[2]), float(z[3])),
                score=score,
                reason=reason,
            )
            self.anomalies.append(a)
            return a

        return None
