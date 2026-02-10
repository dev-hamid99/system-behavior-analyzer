from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ScanPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("System Scanner")
        title.setObjectName("Title")
        subtitle = QLabel("Run quick or full scans across services, startup, tasks, storage, and network.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Recommended workflow: Quick Scan → Review Risks → Apply Actions"))
        layout.addStretch(1)
