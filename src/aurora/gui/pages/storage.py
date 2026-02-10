from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StoragePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("Storage Maintenance")
        title.setObjectName("Title")
        subtitle = QLabel("Cleanup temporary data and reclaim space with rollback-aware actions.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
