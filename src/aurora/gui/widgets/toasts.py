from __future__ import annotations

from PySide6.QtWidgets import QMessageBox, QWidget


def toast(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.information(parent, title, message)
