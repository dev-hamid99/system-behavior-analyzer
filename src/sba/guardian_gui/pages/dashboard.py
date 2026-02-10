from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Deque
from collections import deque
import math
import time

from PySide6.QtCore import (
    Qt,
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    QPoint,
    Property,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QPainterPath,
)
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)



# ==========================================================
#  Config
# ==========================================================
@dataclass(frozen=True)
class UiConfig:
    radius: int = 18
    pad_x: int = 16
    pad_y: int = 14
    gap: int = 12

    history_len: int = 120
    sparkline_height: int = 70

    warn_cpu: float = 70.0
    crit_cpu: float = 85.0

    warn_ram: float = 70.0
    crit_ram: float = 85.0

    warn_disk: float = 80.0
    crit_disk: float = 90.0

    warn_net_kbps: float = 500.0
    crit_net_kbps: float = 900.0

    kpi_anim_ms: int = 420
    hover_anim_ms: int = 140


CFG = UiConfig()


def _is_finite(x: Optional[float]) -> bool:
    if x is None:
        return False
    try:
        return math.isfinite(float(x))
    except Exception:
        return False


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def pct_or_none(x: Optional[float]) -> Optional[float]:
    if not _is_finite(x):
        return None
    return clamp(float(x), 0.0, 100.0)


def kind_for(v: Optional[float], warn: float, crit: float) -> str:
    if not _is_finite(v):
        return "neutral"
    v = float(v)
    if v >= crit:
        return "crit"
    if v >= warn:
        return "warn"
    return "ok"


@dataclass(frozen=True)
class Health:
    label: str
    emoji: str
    hint: str
    level: str  # neutral | ok | warn | crit


def compute_health(cpu: Optional[float], ram: Optional[float], disk: Optional[float]) -> Health:
    cpu_v = float(cpu) if _is_finite(cpu) else 0.0
    ram_v = float(ram) if _is_finite(ram) else 0.0
    disk_v = float(disk) if _is_finite(disk) else 0.0

    worst = max(cpu_v, ram_v, disk_v)
    if (cpu is None and ram is None and disk is None) or worst <= 0:
        return Health("Waiting", "⚪", "Waiting for metrics…", "neutral")

    if worst < 70:
        return Health(
            label="System Stable",
            emoji="🟢",
            hint="No critical spikes detected. Keep collecting samples to strengthen the baseline.",
            level="ok",
        )
    if worst < 85:
        return Health(
            label="System Warning",
            emoji="🟡",
            hint="Some metrics are rising. Check active processes or recent changes.",
            level="warn",
        )
    return Health(
        label="System Critical",
        emoji="🔴",
        hint="High load detected. Investigate CPU/RAM/Disk usage now (Task Manager / Resource Monitor).",
        level="crit",
    )


def add_shadow(widget: QWidget, radius: int = 28, y: int = 10, alpha: int = 90) -> None:
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(radius)
    eff.setXOffset(0)
    eff.setYOffset(y)
    eff.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(eff)


# ==========================================================
#  Premium widgets (Theme-first)
# ==========================================================
class Pill(QLabel):
    def __init__(self, text: str, kind: str = "neutral") -> None:
        super().__init__(text)
        self.setObjectName("Pill")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(30)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.set_kind(kind)

    def set_kind(self, kind: str) -> None:
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class HoverCard(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self._lift_px = 0
        self._anim = QPropertyAnimation(self, b"lift")
        self._anim.setDuration(CFG.hover_anim_ms)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(CFG.pad_x, CFG.pad_y, CFG.pad_x, CFG.pad_y)
        self.lay.setSpacing(10)

        add_shadow(self, radius=22, y=8, alpha=80)

    def get_lift(self) -> int:
        return self._lift_px

    def set_lift(self, v: int) -> None:
        self._lift_px = int(v)
        self.update()

    lift = Property(int, get_lift, set_lift)

    def enterEvent(self, e) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._lift_px)
        self._anim.setEndValue(2)
        self._anim.start()
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setBlurRadius(28)
            eff.setYOffset(10)
            eff.setColor(QColor(0, 0, 0, 95))
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:  # type: ignore[override]
        self._anim.stop()
        self._anim.setStartValue(self._lift_px)
        self._anim.setEndValue(0)
        self._anim.start()
        eff = self.graphicsEffect()
        if isinstance(eff, QGraphicsDropShadowEffect):
            eff.setBlurRadius(22)
            eff.setYOffset(8)
            eff.setColor(QColor(0, 0, 0, 80))
        super().leaveEvent(e)

    def paintEvent(self, e) -> None:  # type: ignore[override]
        # IMPORTANT: don't create a new painter and then call super on the same widget.
        # Instead, we just translate the painter and draw the background ourselves if needed,
        # but QFrame paints via style. The safest: move the widget visually by painting offset.
        if self._lift_px == 0:
            return super().paintEvent(e)

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.save()
        p.translate(0, -self._lift_px)
        # Let Qt style paint into an off-translated painter by rendering the widget:
        # But render() will recurse; so we keep super paint without translation isn't possible.
        # Simpler: just call super (normal) and accept no offset paint on background.
        # Therefore: We'll do a lightweight effect: only translate child painting via QWidget::render
        # without recursion by rendering children region.
        super().paintEvent(e)
        p.restore()


class AnimatedBar(QProgressBar):
    def __init__(self) -> None:
        super().__init__()
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setFixedHeight(10)

        self._anim = QPropertyAnimation(self, b"value")
        self._anim.setDuration(CFG.kpi_anim_ms)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self.set_kind("neutral")

    def set_kind(self, kind: str) -> None:
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_value_smooth(self, target: int) -> None:
        target = int(clamp(target, 0, 100))
        self._anim.stop()
        self._anim.setStartValue(self.value())
        self._anim.setEndValue(target)
        self._anim.start()


class Sparkline(QWidget):
    def __init__(self, height: int = CFG.sparkline_height) -> None:
        super().__init__()
        self.setFixedHeight(height)
        self._data: Deque[float] = deque(maxlen=CFG.history_len)
        self._kind: str = "neutral"

    def set_kind(self, kind: str) -> None:
        self._kind = kind
        self.update()

    def push(self, v: Optional[float]) -> None:
        self._data.append(float(v) if _is_finite(v) else float("nan"))
        self.update()

    def paintEvent(self, e) -> None:  # type: ignore[override]
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect().adjusted(2, 2, -2, -2)

        bg = QColor(7, 14, 26, 90)
        bd = QColor(150, 190, 255, 45)
        p.setPen(QPen(bd, 1))
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(r, 12, 12)

        if not self._data:
            return

        vals = [v for v in self._data if math.isfinite(v)]
        if not vals:
            return
        vmin, vmax = min(vals), max(vals)
        if abs(vmax - vmin) < 1e-6:
            vmax = vmin + 1.0

        line = {
            "neutral": QColor(78, 141, 255, 180),
            "ok": QColor(70, 200, 140, 175),
            "warn": QColor(255, 196, 0, 190),
            "crit": QColor(255, 80, 80, 195),
        }.get(self._kind, QColor(78, 141, 255, 180))

        pr = r.adjusted(10, 10, -10, -10)

        path = QPainterPath()
        n = len(self._data)
        if n < 2:
            return

        def xy(i: int, v: float) -> QPoint:
            x = pr.left() + (pr.width() * (i / (n - 1)))
            t = (v - vmin) / (vmax - vmin)
            y = pr.bottom() - (pr.height() * t)
            return QPoint(int(x), int(y))

        started = False
        for i, v in enumerate(self._data):
            if not math.isfinite(v):
                started = False
                continue
            pt = xy(i, v)
            if not started:
                path.moveTo(pt)
                started = True
            else:
                path.lineTo(pt)

        fill = QPainterPath(path)
        fill.lineTo(pr.right(), pr.bottom())
        fill.lineTo(pr.left(), pr.bottom())
        fill.closeSubpath()

        fill_color = QColor(line)
        fill_color.setAlpha(45)

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(fill_color))
        p.drawPath(fill)

        p.setPen(QPen(line, 2))
        p.setBrush(Qt.NoBrush)
        p.drawPath(path)


class KpiCard(HoverCard):
    def __init__(self, title: str, icon: str) -> None:
        super().__init__()

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(10)

        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 15pt;")

        ttl = QLabel(title)
        ttl.setObjectName("KpiTitle")

        self.pill = Pill("—", "neutral")

        top.addWidget(ico)
        top.addWidget(ttl)
        top.addStretch(1)
        top.addWidget(self.pill)

        self.value = QLabel("—")
        self.value.setObjectName("KpiValue")

        self.hint = QLabel("Waiting for data…")
        self.hint.setObjectName("Muted")

        self.bar = AnimatedBar()

        self.lay.addLayout(top)
        self.lay.addWidget(self.value)
        self.lay.addWidget(self.hint)
        self.lay.addWidget(self.bar)

    def set_value(self, value_text: str, kind: str, hint: str, pct: Optional[float]) -> None:
        self.value.setText(value_text)
        self.hint.setText(hint)

        label = {"neutral": "—", "ok": "OK", "warn": "WARN", "crit": "CRIT"}.get(kind, "—")
        self.pill.setText(label)
        self.pill.set_kind(kind)

        self.bar.set_kind(kind)
        self.bar.set_value_smooth(0 if pct is None else int(clamp(pct, 0.0, 100.0)))


class ChartTile(HoverCard):
    def __init__(self, title: str, subtitle: str = "") -> None:
        super().__init__()
        self.setMinimumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        t = QLabel(title)
        t.setObjectName("SectionTitle")
        s = QLabel(subtitle)
        s.setObjectName("Muted")

        self.spark = Sparkline()
        self.stats = QLabel("—")
        self.stats.setObjectName("Micro")

        self.lay.addWidget(t)
        if subtitle:
            self.lay.addWidget(s)
        self.lay.addWidget(self.spark)
        self.lay.addWidget(self.stats)

    def push(self, v: Optional[float], unit: str = "%") -> None:
        self.spark.push(v)
        finite = [x for x in self.spark._data if math.isfinite(x)]
        if not finite:
            self.stats.setText("—")
            return
        last = finite[-1]
        mn = min(finite)
        mx = max(finite)
        self.stats.setText(f"last {last:.1f}{unit}  •  min {mn:.1f}{unit}  •  max {mx:.1f}{unit}")

    def set_kind(self, kind: str) -> None:
        self.spark.set_kind(kind)


# ==========================================================
#  Dashboard Page
# ==========================================================
class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DashboardRoot")

        self._last_update_ts: Optional[float] = None

        # keep history (if you want it later; sparklines already keep their own history)
        self._cpu_hist: Deque[float] = deque(maxlen=CFG.history_len)
        self._ram_hist: Deque[float] = deque(maxlen=CFG.history_len)
        self._disk_hist: Deque[float] = deque(maxlen=CFG.history_len)
        self._net_hist: Deque[float] = deque(maxlen=CFG.history_len)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(CFG.gap)

        # ==========================
        # HERO
        # ==========================
        self.hero = HoverCard()

        hero_row = QHBoxLayout()
        hero_row.setContentsMargins(0, 0, 0, 0)
        hero_row.setSpacing(14)

        self.health_big = QLabel("🟢 System Stable")
        self.health_big.setObjectName("TitleXL")

        self.health_hint = QLabel("No recent anomalies. Collect data to begin monitoring.")
        self.health_hint.setObjectName("Muted")

        self.last_update = QLabel("Last update: —")
        self.last_update.setObjectName("Muted")

        left = QVBoxLayout()
        left.setSpacing(4)
        left.addWidget(self.health_big)
        left.addWidget(self.health_hint)
        left.addWidget(self.last_update)

        hero_row.addLayout(left, 1)

        pills = QVBoxLayout()
        pills.setSpacing(8)
        pills.setAlignment(Qt.AlignRight | Qt.AlignTop)

        self.p_live = Pill("Live: OFF", "neutral")
        self.p_model = Pill("Model: —", "neutral")
        self.p_data = Pill("Data: —", "neutral")
        self.p_window = Pill(f"Window: last {CFG.history_len}", "neutral")

        pills.addWidget(self.p_live)
        pills.addWidget(self.p_model)
        pills.addWidget(self.p_data)
        pills.addWidget(self.p_window)

        hero_row.addLayout(pills)
        self.hero.lay.addLayout(hero_row)
        root.addWidget(self.hero)

        # ==========================
        # KPI GRID
        # ==========================
        kpi_wrap = QWidget()
        kpi = QGridLayout(kpi_wrap)
        kpi.setContentsMargins(0, 0, 0, 0)
        kpi.setHorizontalSpacing(CFG.gap)
        kpi.setVerticalSpacing(CFG.gap)

        self.k_cpu = KpiCard("CPU", "🧠")
        self.k_ram = KpiCard("RAM", "💾")
        self.k_disk = KpiCard("Disk", "🗄️")
        self.k_net = KpiCard("Network", "📡")

        kpi.addWidget(self.k_cpu, 0, 0)
        kpi.addWidget(self.k_ram, 0, 1)
        kpi.addWidget(self.k_disk, 1, 0)
        kpi.addWidget(self.k_net, 1, 1)

        kpi.setColumnStretch(0, 1)
        kpi.setColumnStretch(1, 1)

        root.addWidget(kpi_wrap)

        # ==========================
        # TRENDS (in the "empty lower area")  ✅ FIXED
        # Build once here, NEVER inside _update_all()
        # ==========================
        lower = QWidget()
        lower_grid = QGridLayout(lower)
        lower_grid.setContentsMargins(0, 0, 0, 0)
        lower_grid.setHorizontalSpacing(CFG.gap)
        lower_grid.setVerticalSpacing(CFG.gap)

        self.trends = HoverCard()

        trends_header = QHBoxLayout()
        trends_header.setContentsMargins(0, 0, 0, 0)
        trends_header.setSpacing(10)

        t_title = QLabel("Trends")
        t_title.setObjectName("SectionTitle")
        t_sub = QLabel("CPU / RAM / Disk / Net history (live sparklines).")
        t_sub.setObjectName("Muted")

        left_hdr = QVBoxLayout()
        left_hdr.setSpacing(2)
        left_hdr.addWidget(t_title)
        left_hdr.addWidget(t_sub)

        trends_header.addLayout(left_hdr, 1)

        self.trends_state = Pill("Waiting for data", "neutral")
        self.trends_state.setMinimumWidth(140)
        trends_header.addWidget(self.trends_state)

        self.trends.lay.addLayout(trends_header)

        tiles_wrap = QWidget()
        tiles = QGridLayout(tiles_wrap)
        tiles.setContentsMargins(0, 0, 0, 0)
        tiles.setHorizontalSpacing(CFG.gap)
        tiles.setVerticalSpacing(CFG.gap)

        self.tile_cpu = ChartTile("CPU %", "recent window")
        self.tile_ram = ChartTile("RAM %", "recent window")
        self.tile_disk = ChartTile("Disk %", "recent window")
        self.tile_net = ChartTile("Net KB/s", "recent window")

        tiles.addWidget(self.tile_cpu, 0, 0)
        tiles.addWidget(self.tile_ram, 0, 1)
        tiles.addWidget(self.tile_disk, 1, 0)
        tiles.addWidget(self.tile_net, 1, 1)

        tiles.setColumnStretch(0, 1)
        tiles.setColumnStretch(1, 1)
        tiles.setRowStretch(0, 1)
        tiles.setRowStretch(1, 1)

        # Make trends scrollable (small screens)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(tiles_wrap)

        self.trends.lay.addWidget(scroll, 1)

        # ✅ This is the critical line that fills the empty area
        lower_grid.addWidget(self.trends, 0, 0)

        lower_grid.setColumnStretch(0, 1)
        lower_grid.setRowStretch(0, 1)

        # give lower area remaining height
        root.addWidget(lower, 1)

        # ==========================
        # Init state
        # ==========================
        self.set_status_badges(live=False, model_ok=False, data_ok=False)
        self._update_all(cpu=None, ram=None, disk=None, net_kbps=None)

        self._ticker = QTimer(self)
        self._ticker.setInterval(800)
        self._ticker.timeout.connect(self._refresh_last_update_label)
        self._ticker.start()

    # --------------------------
    # Public API
    # --------------------------
    def set_status_badges(self, live: bool, model_ok: bool, data_ok: bool) -> None:
        self.p_live.setText("Live: ON" if live else "Live: OFF")
        self.p_live.set_kind("ok" if live else "neutral")

        self.p_model.setText("Model: OK" if model_ok else "Model: —")
        self.p_model.set_kind("ok" if model_ok else "neutral")

        self.p_data.setText("Data: OK" if data_ok else "Data: —")
        self.p_data.set_kind("ok" if data_ok else "neutral")

    def set_window_label(self, text: str) -> None:
        self.p_window.setText(text)

    def push_sample(
        self,
        cpu: Optional[float],
        ram: Optional[float],
        disk: Optional[float],
        net_kbps: Optional[float],
    ) -> None:
        self._last_update_ts = time.time()

        self._cpu_hist.append(float(cpu) if _is_finite(cpu) else float("nan"))
        self._ram_hist.append(float(ram) if _is_finite(ram) else float("nan"))
        self._disk_hist.append(float(disk) if _is_finite(disk) else float("nan"))
        self._net_hist.append(float(net_kbps) if _is_finite(net_kbps) else float("nan"))

        self._update_all(cpu=cpu, ram=ram, disk=disk, net_kbps=net_kbps)

    # --------------------------
    # Internals
    # --------------------------
    def _refresh_last_update_label(self) -> None:
        if self._last_update_ts is None:
            self.last_update.setText("Last update: —")
            return
        dt = max(0.0, time.time() - self._last_update_ts)
        if dt < 2.0:
            s = "just now"
        elif dt < 60.0:
            s = f"{int(dt)}s ago"
        else:
            s = f"{int(dt // 60)}m ago"
        self.last_update.setText(f"Last update: {s}")

    def _update_all(
        self,
        cpu: Optional[float],
        ram: Optional[float],
        disk: Optional[float],
        net_kbps: Optional[float],
    ) -> None:
        cpu_kind = kind_for(cpu, CFG.warn_cpu, CFG.crit_cpu)
        ram_kind = kind_for(ram, CFG.warn_ram, CFG.crit_ram)
        disk_kind = kind_for(disk, CFG.warn_disk, CFG.crit_disk)

        self.k_cpu.set_value(
            value_text=(f"{cpu:.1f}%" if _is_finite(cpu) else "—"),
            kind=cpu_kind,
            hint=("Waiting for data…" if not _is_finite(cpu) else f"Current: {cpu:.1f}%"),
            pct=pct_or_none(cpu),
        )
        self.k_ram.set_value(
            value_text=(f"{ram:.1f}%" if _is_finite(ram) else "—"),
            kind=ram_kind,
            hint=("Waiting for data…" if not _is_finite(ram) else f"Current: {ram:.1f}%"),
            pct=pct_or_none(ram),
        )
        self.k_disk.set_value(
            value_text=(f"{disk:.1f}%" if _is_finite(disk) else "—"),
            kind=disk_kind,
            hint=("Waiting for data…" if not _is_finite(disk) else f"Current: {disk:.1f}%"),
            pct=pct_or_none(disk),
        )

        if not _is_finite(net_kbps):
            self.k_net.set_value("—", "neutral", "Waiting for data…", None)
            net_kind = "neutral"
        else:
            nk = float(net_kbps)
            net_kind = "crit" if nk >= CFG.crit_net_kbps else ("warn" if nk >= CFG.warn_net_kbps else "ok")
            net_pct = clamp(nk / 10.0, 0.0, 100.0)
            self.k_net.set_value(f"{nk:.0f} KB/s", net_kind, f"Current: {nk:.0f} KB/s", net_pct)

        health = compute_health(cpu, ram, disk)
        self.health_big.setText(f"{health.emoji} {health.label}")
        self.health_hint.setText(health.hint)

        any_data = _is_finite(cpu) or _is_finite(ram) or _is_finite(disk) or _is_finite(net_kbps)
        if not any_data:
            self.trends_state.setText("Waiting for data")
            self.trends_state.set_kind("neutral")
        else:
            kinds = [cpu_kind, ram_kind, disk_kind, net_kind]
            if "crit" in kinds:
                self.trends_state.setText("Critical signals")
                self.trends_state.set_kind("crit")
            elif "warn" in kinds:
                self.trends_state.setText("Warning signals")
                self.trends_state.set_kind("warn")
            else:
                self.trends_state.setText("Healthy signals")
                self.trends_state.set_kind("ok")

        # set sparkline colors
        self.tile_cpu.set_kind(cpu_kind)
        self.tile_ram.set_kind(ram_kind)
        self.tile_disk.set_kind(disk_kind)
        self.tile_net.set_kind(net_kind)

        # push data points
        self.tile_cpu.push(cpu, unit="%")
        self.tile_ram.push(ram, unit="%")
        self.tile_disk.push(disk, unit="%")
        self.tile_net.push(net_kbps, unit=" KB/s")
