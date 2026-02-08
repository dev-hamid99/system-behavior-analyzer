from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


def _project_root() -> Path:
    # .../system-behavior-analyzer/src/sba/config.py -> parents[2] = repo root
    return Path(__file__).resolve().parents[2]


ROOT_DIR = _project_root()


class AppConfig(BaseModel):
    sample_interval_sec: int = 5

    # Base dirs (absolute)
    data_dir: Path = ROOT_DIR / "data"
    models_dir: Path = ROOT_DIR / "models"
    logs_dir: Path = ROOT_DIR / "logs"

    # Storage
    parquet_file: Path = data_dir / "metrics.parquet"
    sqlite_file: Path = data_dir / "metrics.sqlite"

    # ML
    model_file: Path = models_dir / "isoforest.joblib"
    random_state: int = 42


config = AppConfig()
