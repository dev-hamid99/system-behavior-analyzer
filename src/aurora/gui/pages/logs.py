from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LogsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Audit log and export report."))
