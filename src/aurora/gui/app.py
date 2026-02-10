from __future__ import annotations

import sys
import traceback

from aurora.core.logging import setup_logging
from aurora.gui.theme import stylesheet


def run_gui() -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QApplication

        from aurora.gui.main_window import MainWindow
    except Exception as exc:  # pragma: no cover
        print(f"[aurora.gui] Failed to import GUI modules: {exc!r}", file=sys.stderr)
        traceback.print_exc()
        return 1

    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        setup_logging()
        app = QApplication(sys.argv)

        try:
            app.setStyleSheet(stylesheet(dark=True))
        except Exception as exc:  # pragma: no cover
            print(f"[aurora.gui] Failed to apply theme: {exc!r}", file=sys.stderr)
            traceback.print_exc()

        window = MainWindow()
        window.show()
        return app.exec()
    except Exception as exc:  # pragma: no cover
        print(f"[aurora.gui] GUI startup failed: {exc!r}", file=sys.stderr)
        traceback.print_exc()
        return 1


def main() -> None:
    raise SystemExit(run_gui())
