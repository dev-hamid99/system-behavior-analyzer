from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ["cpu_percent", "mem_percent", "disk_percent", "net_sent_kb_s", "net_recv_kb_s"]


def train_isolation_forest(parquet_path: Path, model_path: Path, random_state: int = 42) -> None:
    df = pd.read_parquet(parquet_path).dropna()
    if df.empty:
        raise ValueError("No data found in parquet. Run collect first.")

    X = df[FEATURES]

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=random_state,
    )
    model.fit(X)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
