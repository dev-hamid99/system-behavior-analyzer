"""Compatibility layer.

The project currently ships a newer, modular GUI under ``sba.guardian_gui``.
The ``sba.gui`` package is kept to avoid breaking imports; it re-exports the
modular implementation.
"""

from __future__ import annotations

from sba.guardian_gui.app import main as main  # noqa: F401
from sba.guardian_gui.main_window import MainWindow as MainWindow  # noqa: F401
from sba.guardian_gui.theme import APP_QSS as APP_QSS, Palette as Palette  # noqa: F401
