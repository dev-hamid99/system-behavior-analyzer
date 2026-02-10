from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def confirm(parent: QWidget, title: str, message: str) -> bool:
    return QMessageBox.question(parent, title, message) == QMessageBox.Yes
