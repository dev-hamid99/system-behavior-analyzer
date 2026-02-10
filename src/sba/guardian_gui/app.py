from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from sba.guardian_gui.main_window import MainWindow
from sba.guardian_gui.theme import APP_QSS


def main() -> None:
    # optional: sharper scaling on Windows
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication.instance() or QApplication(sys.argv)

    # Apply global stylesheet (single source of truth)
    try:
        app.setStyleSheet(APP_QSS)
    except Exception as e:
        print("ERROR applying APP_QSS:", repr(e))
        app.setStyleSheet("")

    w = MainWindow()
    w.setObjectName("AppRoot")  # IMPORTANT: allows QWidget#AppRoot rules to match
    w.show()
    raise SystemExit(app.exec())


def run_gui() -> None:
    """Entrypoint for: python -m sba.guardian_gui"""
    main()


if __name__ == "__main__":
    main()
