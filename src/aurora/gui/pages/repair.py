from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class RepairPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Repair Center")
        title.setObjectName("Title")
        subtitle = QLabel("Guided workflows for slow boot, high CPU, and network stability incidents.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Each workflow follows: Preview → Confirm → Apply → Rollback option."))
        layout.addStretch(1)
