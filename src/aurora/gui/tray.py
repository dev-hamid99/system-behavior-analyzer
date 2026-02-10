from __future__ import annotations

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def build_tray() -> QSystemTrayIcon:
    tray = QSystemTrayIcon()
    menu = QMenu()
    menu.addAction(QAction("Quick Scan", menu))
    menu.addAction(QAction("Gaming Mode", menu))
    menu.addAction(QAction("Quit", menu))
    tray.setContextMenu(menu)
    return tray
