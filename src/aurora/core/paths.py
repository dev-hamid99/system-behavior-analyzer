from __future__ import annotations

from pathlib import Path

from aurora.core.constants import APP_NAME


def app_home() -> Path:
    root = Path.home() / f".{APP_NAME.lower()}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def data_dir() -> Path:
    p = app_home() / "data"
    p.mkdir(parents=True, exist_ok=True)
    return p


def logs_dir() -> Path:
    p = app_home() / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p
