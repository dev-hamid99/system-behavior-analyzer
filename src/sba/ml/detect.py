from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

FEATURES = ["cpu_percent", "mem_percent", "disk_percent", "net_sent_kb_s", "net_recv_kb_s"]


def detect_anomalies(parquet_path: Path, model_path: Path) -> pd.DataFrame:
    df = pd.read_parquet(parquet_path).dropna()
    if df.empty:
        raise ValueError("No data found in parquet. Run collect first.")

    model = joblib.load(model_path)

    X = df[FEATURES]
    pred = model.predict(X)          # -1 anomaly, 1 normal
    score = model.decision_function(X)

    out = df.copy()
    out["is_anomaly"] = (pred == -1)
    out["anomaly_score"] = score
    return out
