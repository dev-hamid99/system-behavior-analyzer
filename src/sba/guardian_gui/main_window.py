from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from sba.guardian_gui.pages.dashboard import DashboardPage
from sba.guardian_gui.pages.anomalies import AnomaliesPage
from sba.guardian_gui.workers.system_worker import SystemWorker, SystemSample
from sba.guardian_gui.core.session import Session, Sample


# ==========================================================
#  Small helpers
# ==========================================================
def set_kind(widget: QWidget, kind: str) -> None:
    widget.setProperty("kind", kind)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


class Pill(QLabel):
    """QSS-driven pill: objectName=Pill, property kind=neutral/ok/warn/crit"""

    def __init__(self, text: str, kind: str = "neutral") -> None:
        super().__init__(text)
        self.setObjectName("Pill")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(30)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        set_kind(self, kind)


class Card(QFrame):
    def __init__(self, strong: bool = False) -> None:
        super().__init__()
        self.setObjectName("CardStrong" if strong else "Card")
        self.setAttribute(Qt.WA_StyledBackground, True)


class Toast(QFrame):
    """Small glass toast shown top-right."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setVisible(False)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        self.icon = QLabel("ℹ️")
        self.msg = QLabel("—")
        self.msg.setWordWrap(True)
        self.msg.setObjectName("Muted")

        lay.addWidget(self.icon)
        lay.addWidget(self.msg, 1)

        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

        self.setFixedWidth(380)

    def show_toast(self, text: str, kind: str = "neutral", ms: int = 2400) -> None:
        self.msg.setText(text)
        self.icon.setText({"ok": "✅", "warn": "⚠️", "crit": "🛑"}.get(kind, "ℹ️"))
        set_kind(self, kind)

        parent = self.parentWidget()
        if parent is None:
            return

        margin = 18
        w = self.width()
        h = self.sizeHint().height()

        end = QRect(parent.width() - w - margin, margin, w, h)
        start = QRect(parent.width() - w - margin, margin - 18, w, h)

        self.setGeometry(start)
        self.setVisible(True)

        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

        self._hide_timer.stop()
        self._hide_timer.start(ms)


class FadeStack(QStackedWidget):
    """Soft fade transition when switching pages."""

    def __init__(self) -> None:
        super().__init__()
        self._overlay = QFrame(self)
        self._overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._overlay.setStyleSheet("background: rgba(7, 14, 26, 0.55);")
        self._overlay.hide()

        self._anim = QPropertyAnimation(self._overlay, b"windowOpacity")
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.finished.connect(self._overlay.hide)

    def setCurrentIndex(self, index: int) -> None:  # type: ignore[override]
        if index == self.currentIndex():
            return

        self._overlay.setGeometry(self.rect())
        self._overlay.show()
        self._overlay.setWindowOpacity(0.0)

        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setKeyValueAt(0.35, 1.0)
        self._anim.setEndValue(0.0)
        self._anim.start()

        super().setCurrentIndex(index)

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        self._overlay.setGeometry(self.rect())


@dataclass(frozen=True)
class PageMeta:
    title: str
    subtitle: str


# ==========================================================
#  MainWindow
# ==========================================================
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("System Guardian AI")

        self.setMinimumSize(1060, 680)
        self.resize(1320, 820)

        # Live worker + session
        self._sys_worker: Optional[SystemWorker] = None
        self.session = Session()

        # Root
        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        # Sidebar
        self.sidebar = self._build_sidebar()
        root_layout.addWidget(self.sidebar)

        # Right area
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(12)
        root_layout.addWidget(right, 1)

        # Topbar
        self.topbar = self._build_topbar()
        right_layout.addWidget(self.topbar)

        # Pages
        self.pages = FadeStack()
        right_layout.addWidget(self.pages, 1)

        self.dashboard = DashboardPage()
        self.anomalies_page = AnomaliesPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.anomalies_page)
        self.pages.addWidget(self._placeholder_page("Assistant", "Coming next: chat + explanations + guided actions"))
        self.pages.addWidget(self._placeholder_page("Settings", "Coming next: paths, preferences, diagnostics"))

        # Toast overlay
        self.toast = Toast(right)
        self.toast.raise_()

        # Meta
        self._meta = [
            PageMeta("Dashboard", "Live overview and system health"),
            PageMeta("Anomalies", "Review detected anomalies"),
            PageMeta("Assistant", "Ask Guardian for explanations & tips"),
            PageMeta("Settings", "Paths, preferences, and diagnostics"),
        ]
        self._apply_page_meta(0)

        # Wire nav
        for i, btn in enumerate(self._nav_buttons):
            btn.clicked.connect(lambda _=False, idx=i: self._go(idx))

        # Wire actions
        self.btn_collect.clicked.connect(self._toggle_collect)
        self.btn_train.clicked.connect(self._train_model)
        self.btn_detect.clicked.connect(self._detect_now)

        # Anomalies: clear button
        self.anomalies_page.btn_clear.clicked.connect(self._clear_anomalies)

        self._refresh_ui_state()
        self._go(0)

    # -------------------------
    # Build UI
    # -------------------------
    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(270)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        # Brand card
        brand = Card(strong=True)
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(14, 12, 14, 12)
        bl.setSpacing(6)

        title = QLabel("Guardian AI")
        title.setObjectName("Title")
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title.setMinimumWidth(0)
        title.setWordWrap(False)

        subtitle = QLabel("Monitoring • Anomalies • Explanations")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(False)

        badge = Pill("Live", "neutral")
        badge.hide()
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(30)
        badge.setMinimumWidth(64)
        badge.setMaximumWidth(90)

# Row: title left, badge right
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        row.addWidget(title, 1)      # title takes remaining space
        row.addWidget(badge, 0)      # badge keeps size

        bl.addLayout(row)

# Subtitle below, with a tiny top margin
        subtitle.setContentsMargins(0, 2, 0, 0)
        bl.addWidget(subtitle)

        lay.addWidget(brand)


        self._nav_buttons: list[QPushButton] = []
        nav_wrap = QWidget()
        nav = QVBoxLayout(nav_wrap)
        nav.setContentsMargins(0, 0, 0, 0)
        nav.setSpacing(8)

        for name in ["Dashboard", "Anomalies", "Assistant", "Settings"]:
            b = QPushButton(name)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setObjectName("NavItem")
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.setMinimumHeight(44)
            self._nav_buttons.append(b)
            nav.addWidget(b)

        nav.addStretch(1)
        lay.addWidget(nav_wrap, 1)

        foot = Card()
        fl = QVBoxLayout(foot)
        fl.setContentsMargins(14, 12, 14, 12)
        fl.setSpacing(4)

        self.sb_state = QLabel("Status: idle")
        self.sb_state.setObjectName("Muted")
        self.sb_model = QLabel("Model: —")
        self.sb_model.setObjectName("Muted")
        self.sb_data = QLabel("Samples: 0")
        self.sb_data.setObjectName("Muted")

        fl.addWidget(self.sb_state)
        fl.addWidget(self.sb_model)
        fl.addWidget(self.sb_data)

        lay.addWidget(foot)

        return sidebar

    def _build_topbar(self) -> QWidget:
        topbar = QFrame()
        topbar.setObjectName("Topbar")

        lay = QHBoxLayout(topbar)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(10)

        self.h_title = QLabel("Dashboard")
        self.h_title.setObjectName("SectionTitle")
        self.h_subtitle = QLabel("Live overview and system health")
        self.h_subtitle.setObjectName("Muted")

        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        left.setSpacing(2)
        left.addWidget(self.h_title)
        left.addWidget(self.h_subtitle)
        lay.addLayout(left, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search… (process, anomaly, metric)")
        self.search.setMaximumWidth(360)
        lay.addWidget(self.search)

        self.p_state = Pill("Ready", "neutral")
        lay.addWidget(self.p_state)

        self.btn_collect = QPushButton("Collect")
        self.btn_train = QPushButton("Train")
        self.btn_detect = QPushButton("Detect")
        self.btn_detect.setObjectName("Primary")

        lay.addWidget(self.btn_collect)
        lay.addWidget(self.btn_train)
        lay.addWidget(self.btn_detect)

        return topbar

    def _placeholder_page(self, title: str, subtitle: str) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(12)

        card = Card()
        c = QVBoxLayout(card)
        c.setContentsMargins(18, 16, 18, 16)
        c.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("TitleXL")
        s = QLabel(subtitle)
        s.setObjectName("Muted")

        c.addWidget(t)
        c.addWidget(s)
        c.addSpacing(10)

        hint = QLabel("This page is intentionally empty until the next module lands.")
        hint.setObjectName("Muted")
        c.addWidget(hint)

        l.addWidget(card)
        l.addStretch(1)
        return w

    # -------------------------
    # Navigation
    # -------------------------
    def _go(self, idx: int) -> None:
        idx = max(0, min(idx, self.pages.count() - 1))
        for i, b in enumerate(self._nav_buttons):
            b.setChecked(i == idx)
        self.pages.setCurrentIndex(idx)
        self._apply_page_meta(idx)

    def _apply_page_meta(self, idx: int) -> None:
        if 0 <= idx < len(self._meta):
            m = self._meta[idx]
            self.h_title.setText(m.title)
            self.h_subtitle.setText(m.subtitle)

    # -------------------------
    # Collect
    # -------------------------
    def _toggle_collect(self) -> None:
        if self._sys_worker is None:
            self._start_collect()
        else:
            self._stop_collect()

    def _start_collect(self) -> None:
        self._toast("Live collect started", "ok")
        self.sb_state.setText("Status: live collecting")

        self.p_state.setText("Live")
        set_kind(self.p_state, "ok")

        self.dashboard.set_status_badges(
            live=True,
            model_ok=(self.session.model is not None),
            data_ok=True,
        )

        self._sys_worker = SystemWorker(interval_s=1.0, disk_path="C:\\")
        self._sys_worker.sample.connect(self._on_system_sample)
        self._sys_worker.error.connect(lambda msg: self._toast(f"Collector error: {msg}", "crit"))
        self._sys_worker.start()

        self.btn_collect.setText("Stop")

    def _stop_collect(self) -> None:
        if self._sys_worker is None:
            return

        self._toast("Live collect stopped", "warn")
        self.sb_state.setText("Status: idle")

        self.p_state.setText("Ready")
        set_kind(self.p_state, "neutral")

        self.dashboard.set_status_badges(
            live=False,
            model_ok=(self.session.model is not None),
            data_ok=(self.session.count() > 0),
        )

        self._sys_worker.stop()
        self._sys_worker.wait(1500)
        self._sys_worker = None

        self.btn_collect.setText("Collect")

    def _on_system_sample(self, s: SystemSample) -> None:
        # store
        self.session.add(Sample(ts=s.ts, cpu=s.cpu, ram=s.ram, disk=s.disk, net_kbps=s.net_kbps))
        self.sb_data.setText(f"Samples: {self.session.count()}")

        # update dashboard UI
        self.dashboard.push_sample(cpu=s.cpu, ram=s.ram, disk=s.disk, net_kbps=s.net_kbps)

        # optionally auto-detect if model exists (lightweight)
        if self.session.model is not None:
            a = self.session.detect_last(z_thresh=3.0)
            if a is not None:
                self._on_anomaly(a)

    # -------------------------
    # Train / Detect
    # -------------------------
    def _train_model(self) -> None:
        min_samples = 60
        if not self.session.can_train(min_samples=min_samples):
            self._toast(f"Need more data to train (have {self.session.count()}, need {min_samples}+)", "warn")
            return

        # Train on last 300 samples (more reactive). You can set None for all.
        m = self.session.train(window=300)

        self.sb_model.setText(f"Model: OK (n={m.trained_on})")
        self.dashboard.set_status_badges(
            live=(self._sys_worker is not None),
            model_ok=True,
            data_ok=True,
        )

        self._toast("Model trained (baseline ready)", "ok")

    def _detect_now(self) -> None:
        if not self.session.can_detect():
            self._toast("Train the model first", "warn")
            return

        a = self.session.detect_last(z_thresh=3.0)
        if a is None:
            self._toast("No anomaly (last sample OK)", "ok")
            self.sb_state.setText("Status: normal")
            self.p_state.setText("Ready")
            set_kind(self.p_state, "ok")
            return

        self._on_anomaly(a)

    def _on_anomaly(self, a) -> None:
        self._toast(f"Anomaly detected • {a.reason} • score={a.score:.2f}", "crit")
        self.sb_state.setText("Status: anomaly detected")
        self.p_state.setText("Alert")
        set_kind(self.p_state, "crit")

        # push into anomalies page
        self.anomalies_page.append_anomaly(a)

        # also move badges
        self.dashboard.set_status_badges(
            live=(self._sys_worker is not None),
            model_ok=True,
            data_ok=True,
        )

    def _clear_anomalies(self) -> None:
        self.session.anomalies.clear()
        self.anomalies_page.set_anomalies([])
        self._toast("Anomalies cleared", "ok")

    def _refresh_ui_state(self) -> None:
        self.sb_data.setText(f"Samples: {self.session.count()}")
        self.sb_model.setText("Model: —")
        self.dashboard.set_status_badges(live=False, model_ok=False, data_ok=False)

    # -------------------------
    # Toast + Resize + Close
    # -------------------------
    def _toast(self, text: str, kind: str = "neutral") -> None:
        self.toast.show_toast(text, kind=kind, ms=2600)
        self.sb_state.setText(f"Status: {text}")

    def resizeEvent(self, e) -> None:  # type: ignore[override]
        super().resizeEvent(e)
        if self.toast.isVisible():
            self.toast.show_toast(
                self.toast.msg.text(),
                kind=self.toast.property("kind") or "neutral",
                ms=1800,
            )

    def closeEvent(self, e) -> None:  # type: ignore[override]
        if self._sys_worker is not None:
            self._sys_worker.stop()
            self._sys_worker.wait(1500)
            self._sys_worker = None
        super().closeEvent(e)
