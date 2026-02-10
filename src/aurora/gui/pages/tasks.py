from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TasksPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Scheduled tasks management."))
