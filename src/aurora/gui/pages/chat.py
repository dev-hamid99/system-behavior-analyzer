from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ChatPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("PageRoot")
        layout = QVBoxLayout(self)
        title = QLabel("AURORA AI Copilot")
        title.setObjectName("Title")
        subtitle = QLabel("Explain findings, generate fix plans, and request guided diagnostics.")
        subtitle.setObjectName("Muted")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Copilot never applies system actions without explicit user confirmation."))
        layout.addStretch(1)
