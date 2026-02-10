from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StartupPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Startup Manager")
        title.setObjectName("Title")
        subtitle = QLabel("Review startup entries and apply safe toggles for boot-time performance.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
