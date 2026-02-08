from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sba.config import config
from sba.logging_config import setup_logging
from sba.ml.detect import detect_anomalies
from sba.ml.train import train_isolation_forest

logger = logging.getLogger("sba")


def train(
    parquet: Optional[Path] = None,
    model: Optional[Path] = None,
) -> None:
    """
    Train IsolationForest model from Parquet metrics.
    Called by Typer command in app.py.
    """
    setup_logging(config.logs_dir)

    parquet_file = parquet or config.parquet_file
    model_file = model or config.model_file

    logger.info("Training model | parquet=%s | model=%s", parquet_file, model_file)
    train_isolation_forest(parquet_file, model_file)
    print(f"✅ Model trained and saved to {model_file}")


def detect(
    limit: int = 30,
    parquet: Optional[Path] = None,
    model: Optional[Path] = None,
) -> None:
    """
    Detect anomalies using trained model.
    Called by Typer command in app.py.
    """
    setup_logging(config.logs_dir)

    parquet_file = parquet or config.parquet_file
    model_file = model or config.model_file

    if not model_file.exists():
        raise FileNotFoundError(
            f"Model not found: {model_file}. Run `sba train` first (after collecting data)."
        )

    logger.info("Detect anomalies | parquet=%s | model=%s | limit=%s", parquet_file, model_file, limit)
    df = detect_anomalies(parquet_file, model_file)

    print(f"anomalies: {int(df['is_anomaly'].sum())}")

    if limit > 0:
        print(df.tail(limit).to_string(index=False))
