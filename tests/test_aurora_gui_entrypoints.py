from __future__ import annotations

from aurora.gui import app as gui_app


def test_aurora_gui_symbols_exist() -> None:
    assert callable(gui_app.run_gui)
    assert callable(gui_app.main)
