from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ServicesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Services Control")
        title.setObjectName("Title")
        subtitle = QLabel("Operate on safe service presets with explicit risk visibility.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
