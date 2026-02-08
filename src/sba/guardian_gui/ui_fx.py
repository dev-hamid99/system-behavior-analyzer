from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def add_shadow(widget: QWidget, radius: int = 26, y: int = 8, alpha: int = 90) -> None:
    """
    Adds a soft shadow under a widget (premium 'elevation' effect).
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(radius)
    shadow.setXOffset(0)
    shadow.setYOffset(y)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
