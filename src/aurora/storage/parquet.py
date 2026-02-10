from __future__ import annotations

from pathlib import Path

import pandas as pd


class ParquetStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, rows: list[dict[str, object]]) -> None:
        pd.DataFrame(rows).to_parquet(self.path, index=False)
