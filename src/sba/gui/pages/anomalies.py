from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AnomaliesPage(QWidget):
    """Simple placeholder page.

    The fully featured GUI pages are being consolidated under ``sba.guardian_gui``.
    """

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        title = QLabel("Anomalies")
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        body = QLabel("Coming next: timeline + filters + detail panel")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title)
        layout.addWidget(body, 1)
