from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LogsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Logs & History")
        title.setObjectName("Title")
        subtitle = QLabel("Audit trail of scans, recommendations, and actions.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
