from __future__ import annotations

import sys
import traceback

from sba.guardian_gui.theme import APP_QSS


def _apply_theme(app: object) -> None:
    try:
        app.setStyleSheet(APP_QSS)
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"[sba.guardian_gui] ERROR: failed to apply APP_QSS: {exc!r}", file=sys.stderr)
        traceback.print_exc()
        app.setStyleSheet("")


def run_gui() -> int:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    # Optional Windows-friendly HiDPI settings
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    _apply_theme(app)

    # Lazy import to keep import side effects minimal for entrypoint checks/tests.
    from sba.guardian_gui.main_window import MainWindow

    window = MainWindow()
    window.setObjectName("AppRoot")
    window.show()
    return app.exec()


def main() -> None:
    raise SystemExit(run_gui())


if __name__ == "__main__":
    main()
