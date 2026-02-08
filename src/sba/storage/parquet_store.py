from __future__ import annotations

from pathlib import Path

import pandas as pd


def append_metrics_parquet(parquet_path: Path, row: dict) -> None:
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    df_new = pd.DataFrame([row])

    if parquet_path.exists():
        df_old = pd.read_parquet(parquet_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_parquet(parquet_path, index=False)
