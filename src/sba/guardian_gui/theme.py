from __future__ import annotations

from dataclasses import dataclass

print("THEME LOADED:", __file__)

@dataclass(frozen=True)
class Palette:
    # Base
    bg: str = "#070E1A"
    bg2: str = "#060B14"

    # Surfaces
    panel: str = "#0B1730"
    panel2: str = "#081428"
    glass: str = "rgba(14, 22, 40, 0.70)"

    # Text
    text: str = "#EAF2FF"
    text2: str = "#CFE2FF"
    muted: str = "#9BB0D3"
    faint: str = "rgba(155, 176, 211, 0.60)"

    # Accents
    primary: str = "#4E8DFF"
    primary2: str = "#2C66F2"
    ring: str = "rgba(78, 141, 255, 0.60)"

    # Semantic
    ok: str = "#46C88C"
    warn: str = "#FFC400"
    crit: str = "#FF5050"

    # Lines / borders
    stroke: str = "rgba(150, 190, 255, 0.14)"
    stroke2: str = "rgba(150, 190, 255, 0.22)"
    stroke3: str = "rgba(150, 190, 255, 0.30)"


PAL = Palette()

APP_QSS = f"""
/* =======================================================================
   PREMIUM THEME (Guardian) - REPAIRED / RESPONSIVE-FRIENDLY
   ======================================================================= */

/* GLOBAL */
* {{
  color: {PAL.text};
  font-family: "Segoe UI";
  font-size: 11pt;                /* slightly smaller for small screens */
}}

QMainWindow, QWidget#AppRoot {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
    stop:0 {PAL.bg}, stop:1 {PAL.bg2}
  );
}}

/* Make labels shrink properly inside layouts (IMPORTANT for overlap issues) */
QLabel {{
  min-width: 0px;
}}

/* Tooltips */
QToolTip {{
  background: rgba(11, 23, 48, 0.92);
  border: 1px solid {PAL.stroke2};
  padding: 6px 8px;
  border-radius: 10px;
}}

/* -------------------------
   Typography system
   ------------------------- */
QLabel#TitleXL {{
  font-size: 20pt;
  font-weight: 800;
  letter-spacing: 0.2px;
  color: {PAL.text};
}}

QLabel#Title {{
  font-size: 18pt;                /* was 20pt -> reduces collisions */
  font-weight: 800;
  letter-spacing: 0.2px;
  color: {PAL.text};
}}

QLabel#Subtitle {{
  color: {PAL.muted};
  margin-top: 2px;
}}

QLabel#SectionTitle {{
  font-size: 12.2pt;
  font-weight: 750;
  color: {PAL.text};
}}

QLabel#Muted {{
  color: {PAL.muted};
}}

QLabel#Micro {{
  font-size: 9.5pt;
  color: {PAL.faint};
}}

/* -------------------------
   Sidebar / Topbar
   ------------------------- */
QFrame#Sidebar {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(8, 26, 54, 0.98),
    stop:1 rgba(7, 18, 38, 0.98)
  );
  border-right: 1px solid rgba(150, 190, 255, 0.10);
}}

QFrame#Topbar {{
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 rgba(12, 28, 55, 0.62),
    stop:1 rgba(7, 14, 26, 0.18)
  );
  border: 1px solid {PAL.stroke};
  border-radius: 18px;
}}

/* -------------------------
   Cards
   ------------------------- */
QFrame#Card {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(13, 30, 60, 0.92),
    stop:1 rgba(9, 22, 46, 0.92)
  );
  border: 1px solid {PAL.stroke};
  border-radius: 18px;
}}

QFrame#Card:hover {{
  border: 1px solid {PAL.stroke2};
}}

QFrame#CardStrong {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(18, 42, 86, 0.92),
    stop:1 rgba(9, 24, 52, 0.92)
  );
  border: 1px solid {PAL.stroke2};
  border-radius: 18px;
}}

/* -------------------------
   Pills / badges
   ------------------------- */
QLabel#Pill {{
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(78, 141, 255, 0.14);
  border: 1px solid rgba(78, 141, 255, 0.22);
  color: {PAL.text};
  font-weight: 750;
  letter-spacing: 0.2px;

  /* IMPORTANT: make pill stable in tight spaces */
  min-width: 56px;
  max-width: 140px;
}}

QLabel#Pill[kind="neutral"] {{
  background: rgba(78, 141, 255, 0.14);
  border: 1px solid rgba(78, 141, 255, 0.22);
}}

QLabel#Pill[kind="ok"] {{
  background: rgba(70, 200, 140, 0.14);
  border: 1px solid rgba(70, 200, 140, 0.26);
  color: rgba(233, 255, 245, 1.0);
}}

QLabel#Pill[kind="warn"] {{
  background: rgba(255, 196, 0, 0.14);
  border: 1px solid rgba(255, 196, 0, 0.28);
  color: rgba(255, 247, 214, 1.0);
}}

QLabel#Pill[kind="crit"] {{
  background: rgba(255, 80, 80, 0.14);
  border: 1px solid rgba(255, 80, 80, 0.30);
  color: rgba(255, 229, 229, 1.0);
}}

/* -------------------------
   Inputs
   ------------------------- */
QLineEdit, QTextEdit, QPlainTextEdit {{
  background: rgba(7, 22, 47, 0.95);
  border: 1px solid rgba(150, 190, 255, 0.20);
  border-radius: 14px;
  padding: 10px 12px;
  selection-background-color: rgba(78, 141, 255, 0.35);
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
  border: 1px solid {PAL.ring};
}}

/* -------------------------
   Buttons
   ------------------------- */
QPushButton {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(22, 52, 101, 0.95),
    stop:1 rgba(12, 32, 66, 0.95)
  );
  border: 1px solid rgba(160, 210, 255, 0.22);
  padding: 10px 12px;            /* a bit tighter */
  border-radius: 14px;
  font-weight: 700;
}}

QPushButton:hover {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(30, 70, 135, 0.95),
    stop:1 rgba(14, 40, 83, 0.95)
  );
  border: 1px solid rgba(160, 210, 255, 0.34);
}}

QPushButton:pressed {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(14, 40, 83, 0.95),
    stop:1 rgba(10, 28, 59, 0.95)
  );
}}

QPushButton#Primary {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 {PAL.primary}, stop:1 {PAL.primary2}
  );
  border: 1px solid rgba(78, 141, 255, 1.0);
  font-weight: 800;
}}

QPushButton#Primary:hover {{
  background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
    stop:0 rgba(95, 160, 255, 1.0), stop:1 rgba(44, 102, 242, 1.0)
  );
}}

/* -------------------------
   NAV BUTTONS
   ------------------------- */
QPushButton#NavItem {{
  text-align: left;
  padding: 10px 12px;
  border-radius: 14px;
  background: transparent;
  border: 1px solid transparent;
  font-weight: 700;
  color: #D7E8FF;
}}

QPushButton#NavItem:hover {{
  background: rgba(78, 141, 255, 0.10);
  border: 1px solid rgba(78, 141, 255, 0.18);
}}

QPushButton#NavItem:checked {{
  background: rgba(78, 141, 255, 0.20);
  border: 1px solid rgba(78, 141, 255, 0.30);
}}

/* -------------------------
   ProgressBar
   ------------------------- */
QProgressBar {{
  background: rgba(150, 190, 255, 0.10);
  border: 1px solid rgba(150, 190, 255, 0.16);
  border-radius: 6px;
  text-align: center;
}}

QProgressBar::chunk {{
  background: rgba(78, 141, 255, 0.75);
  border-radius: 6px;
}}

QProgressBar[kind="ok"]::chunk {{
  background: rgba(70, 200, 140, 0.70);
}}
QProgressBar[kind="warn"]::chunk {{
  background: rgba(255, 196, 0, 0.76);
}}
QProgressBar[kind="crit"]::chunk {{
  background: rgba(255, 80, 80, 0.78);
}}

/* -------------------------
   ScrollArea / Scrollbars
   ------------------------- */
QScrollArea {{
  background: transparent;
  border: 0px;
}}

QScrollArea > QWidget > QWidget {{
  background: transparent;
}}

QScrollBar:vertical {{
  width: 10px;
  background: transparent;
  margin: 6px 4px 6px 0px;
}}

QScrollBar::handle:vertical {{
  background: rgba(150, 190, 255, 0.20);
  border-radius: 999px;
  min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
  background: rgba(150, 190, 255, 0.30);
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
  height: 0px;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
  background: transparent;
}}
"""
