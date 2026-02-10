from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    bg: str
    bg_alt: str
    panel: str
    panel_alt: str
    stroke: str
    text: str
    text_muted: str
    primary: str
    primary_alt: str
    ok: str
    warn: str
    danger: str


DARK = Palette(
    bg="#0A0F1A",
    bg_alt="#0D1526",
    panel="#121C32",
    panel_alt="#0F1A2D",
    stroke="#223758",
    text="#EAF1FF",
    text_muted="#9FB4D4",
    primary="#4F7DFF",
    primary_alt="#38C8FF",
    ok="#3BCF8E",
    warn="#FFB547",
    danger="#FF5F73",
)

LIGHT = Palette(
    bg="#F3F7FF",
    bg_alt="#EAF1FF",
    panel="#FFFFFF",
    panel_alt="#F8FBFF",
    stroke="#CFDDF5",
    text="#14233D",
    text_muted="#5A7194",
    primary="#3F69F0",
    primary_alt="#2DAAD8",
    ok="#1EAB73",
    warn="#D38A09",
    danger="#CF3C50",
)


def _qss(p: Palette) -> str:
    return f"""
    * {{
      color: {p.text};
      font-family: "Segoe UI", "Inter";
      font-size: 10.5pt;
    }}

    QMainWindow, QWidget#AuroraRoot {{
      background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {p.bg}, stop:1 {p.bg_alt});
    }}

    QFrame#Sidebar {{
      background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {p.panel}, stop:1 {p.panel_alt});
      border-right: 1px solid {p.stroke};
    }}

    QFrame#Topbar, QFrame#Card {{
      background: {p.panel};
      border: 1px solid {p.stroke};
      border-radius: 14px;
    }}

    QLabel#Title {{
      font-size: 16pt;
      font-weight: 800;
      color: {p.text};
    }}

    QLabel#Muted {{
      color: {p.text_muted};
    }}

    QPushButton {{
      background: {p.panel_alt};
      color: {p.text};
      border: 1px solid {p.stroke};
      border-radius: 10px;
      padding: 8px 10px;
      font-weight: 600;
    }}

    QPushButton:hover {{
      border: 1px solid {p.primary};
    }}

    QPushButton#Primary {{
      background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {p.primary}, stop:1 {p.primary_alt});
      color: #FFFFFF;
      border: 1px solid {p.primary};
      font-weight: 700;
    }}

    QPushButton#NavItem {{
      text-align: left;
      padding: 10px 12px;
      border-radius: 10px;
      background: transparent;
    }}

    QPushButton#NavItem:checked {{
      background: rgba(79, 125, 255, 0.18);
      border: 1px solid {p.primary};
    }}

    QWidget#PageRoot {{
      background: transparent;
    }}
    """


def stylesheet(dark: bool) -> str:
    return _qss(DARK if dark else LIGHT)
