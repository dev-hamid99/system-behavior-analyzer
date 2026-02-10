from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BoosterPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Gaming / Work / Battery profile controls."))
