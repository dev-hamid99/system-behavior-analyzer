from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StartupPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Startup apps management."))
