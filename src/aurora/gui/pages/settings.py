from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Settings")
        title.setObjectName("Title")
        subtitle = QLabel("Theme, startup, privacy, and diagnostics preferences.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Default mode: Dark. Light mode can be enabled any time."))
        layout.addStretch(1)
