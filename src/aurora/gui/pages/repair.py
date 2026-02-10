from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class RepairPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Repair Wizards: Slow boot, High CPU, Network."))
