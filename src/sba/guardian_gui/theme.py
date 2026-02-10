from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    # Backgrounds
    bg: str = "#F4F8FF"
    bg2: str = "#E9F1FF"

    # Surfaces
    panel: str = "#FFFFFF"
    panel_soft: str = "#F7FAFF"

    # Typography
    text: str = "#162033"
    text2: str = "#2A3C57"
    muted: str = "#5B6F8D"
    faint: str = "#8EA0BC"

    # Brand accents
    primary: str = "#5A73FF"
    primary_2: str = "#3F58E6"
    accent: str = "#00A5A5"

    # Semantic
    ok: str = "#1FA971"
    warn: str = "#D48A00"
    crit: str = "#D33D55"

    # Lines
    stroke: str = "#D7E2F2"
    stroke_2: str = "#C6D5EA"


PAL = Palette()

APP_QSS = f"""
* {{
  color: {PAL.text};
  font-family: "Inter", "Segoe UI", "SF Pro Text";
  font-size: 10.5pt;
}}

QMainWindow, QWidget#AppRoot {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 {PAL.bg},
    stop:1 {PAL.bg2}
  );
}}

QToolTip {{
  background: {PAL.panel};
  border: 1px solid {PAL.stroke_2};
  border-radius: 8px;
  padding: 6px 8px;
  color: {PAL.text};
}}

QLabel#TitleXL {{
  font-size: 20pt;
  font-weight: 800;
  color: {PAL.text};
}}

QLabel#Title {{
  font-size: 17pt;
  font-weight: 800;
  color: {PAL.text};
}}

QLabel#Subtitle {{
  color: {PAL.muted};
}}

QLabel#SectionTitle {{
  font-size: 12pt;
  font-weight: 700;
  color: {PAL.text};
}}

QLabel#Muted {{
  color: {PAL.muted};
}}

QLabel#Micro {{
  color: {PAL.faint};
  font-size: 9pt;
}}

QFrame#Sidebar {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 #F2F7FF,
    stop:1 #E8F0FF
  );
  border-right: 1px solid {PAL.stroke};
}}

QFrame#Topbar {{
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid {PAL.stroke};
  border-radius: 16px;
}}

QFrame#Card, QFrame#CardStrong {{
  background: rgba(255, 255, 255, 0.88);
  border: 1px solid {PAL.stroke};
  border-radius: 16px;
}}

QFrame#CardStrong {{
  border: 1px solid {PAL.stroke_2};
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 rgba(255, 255, 255, 0.95),
    stop:1 rgba(238, 245, 255, 0.95)
  );
}}

QLabel#Pill {{
  background: #EEF3FF;
  border: 1px solid {PAL.stroke};
  border-radius: 999px;
  color: {PAL.text2};
  font-size: 9.5pt;
  font-weight: 700;
  padding: 5px 10px;
  min-width: 64px;
}}

QLabel#Pill[kind="neutral"] {{
  background: #EEF3FF;
  border-color: #D6E2F9;
  color: #344963;
}}

QLabel#Pill[kind="ok"] {{
  background: #E9F8F1;
  border-color: #BFEBD8;
  color: {PAL.ok};
}}

QLabel#Pill[kind="warn"] {{
  background: #FFF6E8;
  border-color: #F6D6A3;
  color: {PAL.warn};
}}

QLabel#Pill[kind="crit"] {{
  background: #FFECEF;
  border-color: #F6C2CC;
  color: {PAL.crit};
}}

QLineEdit, QTextEdit, QPlainTextEdit {{
  background: #FFFFFF;
  border: 1px solid {PAL.stroke_2};
  border-radius: 12px;
  padding: 10px 12px;
  color: {PAL.text};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
  border: 1px solid {PAL.primary};
}}

QPushButton {{
  background: #FFFFFF;
  border: 1px solid {PAL.stroke_2};
  border-radius: 12px;
  padding: 9px 12px;
  font-weight: 700;
  color: {PAL.text2};
}}

QPushButton:hover {{
  background: #F4F8FF;
  border-color: #AFC5E8;
}}

QPushButton:pressed {{
  background: #EAF2FF;
}}

QPushButton#Primary {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 {PAL.primary},
    stop:1 {PAL.primary_2}
  );
  color: #FFFFFF;
  border: 1px solid {PAL.primary_2};
}}

QPushButton#Primary:hover {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 #7087FF,
    stop:1 #5069EE
  );
}}

QPushButton#NavItem {{
  text-align: left;
  background: transparent;
  color: {PAL.text2};
  border: 1px solid transparent;
  border-radius: 12px;
  padding: 10px 12px;
}}

QPushButton#NavItem:hover {{
  background: #F3F7FF;
  border-color: #D3DFF1;
}}

QPushButton#NavItem:checked {{
  background: #EAF0FF;
  border-color: #BCCDF3;
  color: {PAL.primary_2};
}}

QProgressBar {{
  background: #EAF0FA;
  border: 1px solid #D9E4F4;
  border-radius: 8px;
  min-height: 10px;
}}

QProgressBar::chunk {{
  border-radius: 7px;
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 {PAL.primary},
    stop:1 {PAL.accent}
  );
}}

QProgressBar[kind="ok"]::chunk {{ background: {PAL.ok}; }}
QProgressBar[kind="warn"]::chunk {{ background: {PAL.warn}; }}
QProgressBar[kind="crit"]::chunk {{ background: {PAL.crit}; }}

QTableWidget {{
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid {PAL.stroke};
  border-radius: 14px;
  gridline-color: #E2EAF6;
  alternate-background-color: #F8FBFF;
}}

QHeaderView::section {{
  background: #F1F6FF;
  border: none;
  border-bottom: 1px solid {PAL.stroke};
  color: {PAL.muted};
  padding: 8px;
  font-weight: 700;
}}

QScrollArea {{
  border: none;
  background: transparent;
}}

QScrollBar:vertical {{
  background: transparent;
  width: 11px;
  margin: 4px;
}}

QScrollBar::handle:vertical {{
  background: #C8D8F1;
  border-radius: 5px;
  min-height: 24px;
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
  height: 0px;
}}
"""
