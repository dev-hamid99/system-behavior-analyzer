from __future__ import annotations

from sba.guardian_gui import app as guardian_app


def test_guardian_gui_entrypoints_are_importable() -> None:
    assert callable(guardian_app.run_gui)
    assert callable(guardian_app.main)
