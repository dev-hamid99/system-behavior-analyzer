from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from aurora.gui.navigation import PAGES
from aurora.gui.pages.booster import BoosterPage
from aurora.gui.pages.chat import ChatPage
from aurora.gui.pages.dashboard import DashboardPage
from aurora.gui.pages.logs import LogsPage
from aurora.gui.pages.repair import RepairPage
from aurora.gui.pages.scan import ScanPage
from aurora.gui.pages.services import ServicesPage
from aurora.gui.pages.settings import SettingsPage
from aurora.gui.pages.startup import StartupPage
from aurora.gui.pages.storage import StoragePage
from aurora.gui.pages.tasks import TasksPage
from aurora.gui.theme import stylesheet


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AURORA - AI PC Guardian")
        self.resize(1360, 860)
        self._dark = True

        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        side_l = QVBoxLayout(sidebar)
        side_l.addWidget(QLabel("AURORA"))

        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {
            "Dashboard": DashboardPage(),
            "Scan": ScanPage(),
            "Booster": BoosterPage(),
            "Repair": RepairPage(),
            "Chat": ChatPage(),
            "Startup": StartupPage(),
            "Services": ServicesPage(),
            "Tasks": TasksPage(),
            "Storage": StoragePage(),
            "Settings": SettingsPage(),
            "Logs": LogsPage(),
        }
        for page_name in PAGES:
            btn = QPushButton(page_name)
            btn.clicked.connect(lambda _=False, name=page_name: self._go(name))
            side_l.addWidget(btn)
            self.stack.addWidget(self.pages[page_name])

        side_l.addStretch(1)

        top = QFrame()
        top.setObjectName("Topbar")
        top_l = QHBoxLayout(top)
        top_l.addWidget(QLabel("Status: Ready"))
        theme_btn = QPushButton("Toggle Dark/Light")
        theme_btn.setObjectName("Primary")
        theme_btn.clicked.connect(self._toggle_theme)
        top_l.addWidget(theme_btn, 0, Qt.AlignRight)

        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.addWidget(top)
        right_l.addWidget(self.stack, 1)

        layout.addWidget(sidebar)
        layout.addWidget(right, 1)

        self._apply_theme()
        self._go("Dashboard")

    def _go(self, page_name: str) -> None:
        self.stack.setCurrentWidget(self.pages[page_name])

    def _toggle_theme(self) -> None:
        self._dark = not self._dark
        self._apply_theme()

    def _apply_theme(self) -> None:
        app = self.window().windowHandle()
        _ = app
        self.setStyleSheet(stylesheet(self._dark))
