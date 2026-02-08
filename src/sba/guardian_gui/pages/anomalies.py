from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QSizePolicy
)

from sba.guardian_gui.core.session import Anomaly


class AnomaliesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Anomalies")
        title.setObjectName("TitleXL")
        sub = QLabel("Detected anomalies (z-score baseline).")
        sub.setObjectName("Muted")
        header_left = QVBoxLayout()
        header_left.addWidget(title)
        header_left.addWidget(sub)

        header.addLayout(header_left, 1)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        header.addWidget(self.btn_clear)

        root.addLayout(header)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Time", "CPU %", "RAM %", "Disk %", "Net KB/s", "Score", "Reason"
        ])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        root.addWidget(self.table, 1)

    def set_anomalies(self, anomalies: List[Anomaly]) -> None:
        self.table.setRowCount(0)
        for a in anomalies:
            self._append_row(a)

    def append_anomaly(self, a: Anomaly) -> None:
        self._append_row(a)

    def _append_row(self, a: Anomaly) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)

        def it(text: str) -> QTableWidgetItem:
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            return item

        self.table.setItem(r, 0, it(self._fmt_time(a.ts)))
        self.table.setItem(r, 1, it(f"{a.cpu:.1f}"))
        self.table.setItem(r, 2, it(f"{a.ram:.1f}"))
        self.table.setItem(r, 3, it(f"{a.disk:.1f}"))
        self.table.setItem(r, 4, it(f"{a.net_kbps:.0f}"))
        self.table.setItem(r, 5, it(f"{a.score:.2f}"))
        self.table.setItem(r, 6, it(a.reason))

        self.table.scrollToBottom()

    @staticmethod
    def _fmt_time(ts: float) -> str:
        # simple local time formatting
        import datetime as dt
        return dt.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
