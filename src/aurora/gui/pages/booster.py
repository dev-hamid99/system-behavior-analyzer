from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BoosterPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Booster Profiles")
        title.setObjectName("Title")
        subtitle = QLabel("Switch between Gaming, Work, and Battery profiles with safe presets.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("All profile actions include preview, risk level, and rollback path."))
        layout.addStretch(1)
