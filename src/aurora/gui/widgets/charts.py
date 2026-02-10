from __future__ import annotations

from PySide6.QtWidgets import QLabel


class PlaceholderChart(QLabel):
    def __init__(self) -> None:
        super().__init__("Live chart placeholder")
