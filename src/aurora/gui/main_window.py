from __future__ import annotations

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
        self.setMinimumSize(1180, 760)
        self.resize(1440, 900)
        self._dark = True

        root = QWidget()
        root.setObjectName("AuroraRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(270)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 14, 14, 14)
        side_layout.setSpacing(8)

        brand = QLabel("AURORA")
        brand.setObjectName("Title")
        subtitle = QLabel("Protect · Diagnose · Optimize")
        subtitle.setObjectName("Muted")
        side_layout.addWidget(brand)
        side_layout.addWidget(subtitle)
        side_layout.addSpacing(8)

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

        self._nav_buttons: list[QPushButton] = []
        for page_name in PAGES:
            button = QPushButton(page_name)
            button.setObjectName("NavItem")
            button.setCheckable(True)
            button.clicked.connect(lambda _=False, name=page_name: self._go(name))
            self._nav_buttons.append(button)
            side_layout.addWidget(button)
            self.stack.addWidget(self.pages[page_name])

        side_layout.addStretch(1)

        topbar = QFrame()
        topbar.setObjectName("Topbar")
        top_layout = QHBoxLayout(topbar)
        top_layout.setContentsMargins(12, 10, 12, 10)

        self.status_label = QLabel("Status: Ready")
        top_layout.addWidget(self.status_label)

        top_layout.addStretch(1)
        theme_button = QPushButton("Dark / Light")
        theme_button.setObjectName("Primary")
        theme_button.clicked.connect(self._toggle_theme)
        top_layout.addWidget(theme_button)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 16, 16, 16)
        right_layout.setSpacing(10)
        right_layout.addWidget(topbar)
        right_layout.addWidget(self.stack, 1)

        layout.addWidget(sidebar)
        layout.addWidget(right, 1)

        self._apply_theme()
        self._go("Dashboard")

    def _go(self, page_name: str) -> None:
        self.stack.setCurrentWidget(self.pages[page_name])
        self.status_label.setText(f"Status: {page_name} ready")
        for button in self._nav_buttons:
            button.setChecked(button.text() == page_name)

    def _toggle_theme(self) -> None:
        self._dark = not self._dark
        self._apply_theme()

    def _apply_theme(self) -> None:
        self.setStyleSheet(stylesheet(self._dark))
