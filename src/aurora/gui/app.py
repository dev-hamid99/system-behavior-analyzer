from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from aurora.core.logging import setup_logging
from aurora.gui.main_window import MainWindow


def run_gui() -> None:
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
