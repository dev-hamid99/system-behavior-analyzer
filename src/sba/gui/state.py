from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class AppState:
    """Lightweight shared state container for GUI pages."""

    df_current: pd.DataFrame
    status_text: str = "Ready"
    last_error: Optional[str] = None
