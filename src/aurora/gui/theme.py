from __future__ import annotations

DARK_QSS = """
QMainWindow { background: #0f1320; }
QFrame#Sidebar { background: #171d2d; border-right: 1px solid #24304a; }
QFrame#Topbar, QFrame#Card { background: #141b2b; border: 1px solid #25334d; border-radius: 12px; }
QPushButton#Primary { background: #4d7cff; color: white; border-radius: 10px; padding: 8px; }
QPushButton { background: #1a2538; color: #e8eefb; border: 1px solid #2d3f60; border-radius: 10px; padding: 8px; }
QLabel { color: #e8eefb; }
"""

LIGHT_QSS = """
QMainWindow { background: #f4f7fd; }
QFrame#Sidebar { background: #edf3ff; border-right: 1px solid #d2def2; }
QFrame#Topbar, QFrame#Card { background: white; border: 1px solid #d7e2f2; border-radius: 12px; }
QPushButton#Primary { background: #4d7cff; color: white; border-radius: 10px; padding: 8px; }
QPushButton { background: white; color: #17233a; border: 1px solid #ccd8ee; border-radius: 10px; padding: 8px; }
QLabel { color: #17233a; }
"""


def stylesheet(dark: bool) -> str:
    return DARK_QSS if dark else LIGHT_QSS
