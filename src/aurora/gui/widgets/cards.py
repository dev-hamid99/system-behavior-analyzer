from __future__ import annotations

from PySide6.QtWidgets import QFrame


class Card(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
