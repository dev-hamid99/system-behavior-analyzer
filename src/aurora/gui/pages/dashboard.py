from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("System Health Overview")
        title.setObjectName("Title")
        subtitle = QLabel("Live posture across CPU, memory, disk, and risk indicators.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Health Score: 92 / 100"))
        layout.addWidget(QLabel("Top Issues: No critical findings in the latest scan."))
        layout.addStretch(1)
