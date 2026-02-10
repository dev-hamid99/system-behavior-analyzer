from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Health Score: --"))
        layout.addWidget(QLabel("Top issues will appear here."))
