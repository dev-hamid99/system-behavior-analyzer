from __future__ import annotations

import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Matplotlib (Charts)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from sba.config import config
from sba.ml.detect import detect_anomalies
from sba.ml.train import train_isolation_forest


# ---------------------------
# Styling (modern-ish)
# ---------------------------
APP_QSS = """
QMainWindow { background: #0b1220; }
* { color: #E6EDF3; font-family: "Segoe UI"; font-size: 10.5pt; }
QFrame#Sidebar { background: #0f1a33; border-right: 1px solid #1f2a44; }
QFrame#Topbar { background: #0b1220; border-bottom: 1px solid #1f2a44; }
QLabel#Title { font-size: 16pt; font-weight: 700; }
QLabel#Subtitle { color: #93a4bf; }

QPushButton {
  background: #1c2a4a;
  border: 1px solid #2b3d66;
  padding: 9px 12px;
  border-radius: 10px;
}
QPushButton:hover { background: #22355f; }
QPushButton:pressed { background: #16223c; }

QPushButton#Primary {
  background: #2b6cff;
  border: 1px solid #2b6cff;
  font-weight: 700;
}
QPushButton#Primary:hover { background: #1f5ef0; }
QPushButton#Danger {
  background: #ff3b3b;
  border: 1px solid #ff3b3b;
  font-weight: 700;
}
QPushButton#Danger:hover { background: #e83434; }

QLineEdit, QTextEdit, QComboBox, QSpinBox {
  background: #0f1a33;
  border: 1px solid #22355f;
  border-radius: 10px;
  padding: 8px;
}
QTextEdit { padding: 10px; }

QFrame#Card {
  background: #0f1a33;
  border: 1px solid #1f2a44;
  border-radius: 14px;
}
QLabel#CardBig { font-size: 18pt; font-weight: 800; }
QLabel#CardSmall { color: #93a4bf; }

QTableWidget {
  background: #0f1a33;
  border: 1px solid #1f2a44;
  border-radius: 14px;
  gridline-color: #1f2a44;
}
QHeaderView::section {
  background: #0b1220;
  border: none;
  padding: 6px;
  color: #93a4bf;
  font-weight: 700;
}
QListWidget {
  background: transparent;
  border: none;
}
QListWidget::item {
  padding: 10px 12px;
  border-radius: 12px;
}
QListWidget::item:selected {
  background: #1c2a4a;
  border: 1px solid #2b3d66;
}
"""


# ---------------------------
# Helpers
# ---------------------------
def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def project_root() -> Path:
    # config.project_root should exist by your earlier setup; fallback if not.
    try:
        return Path(config.project_root)  # type: ignore[attr-defined]
    except Exception:
        # best effort: walk up from this file
        return Path(__file__).resolve().parents[3]


def safe_read_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def run_cmd_in_project(args: list[str]) -> subprocess.CompletedProcess[str]:
    """
    Runs `python -m sba.cli.app ...` in the project folder, capturing output.
    """
    root = project_root()
    return subprocess.run(
        args,
        cwd=str(root),
        capture_output=True,
        text=True,
        shell=False,
    )


# ---------------------------
# Chart widget
# ---------------------------
class MetricChart(QWidget):
    def __init__(self, title: str) -> None:
        super().__init__()
        self.fig = Figure(figsize=(5, 2.2), tight_layout=True)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.title = title

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, df: pd.DataFrame, x: str, y: str) -> None:
        self.ax.clear()
        self.ax.set_title(self.title)
        if not df.empty and x in df.columns and y in df.columns:
            xs = df[x].astype(str).tolist()
            ys = df[y].astype(float).tolist()
            self.ax.plot(xs, ys)
            # keep it readable
            step = max(1, len(xs) // 6)
            self.ax.set_xticks(range(0, len(xs), step))
            self.ax.set_xticklabels([xs[i] for i in range(0, len(xs), step)], rotation=0)
        self.ax.grid(True, alpha=0.2)
        self.canvas.draw_idle()


# ---------------------------
# AI Chat (local command brain)
# ---------------------------
@dataclass
class ChatReply:
    title: str
    body: str


class LocalAssistant:
    """
    Not a cloud LLM.
    It's a local assistant that understands MANY commands and calls your project functions safely.
    """

    def help_text(self) -> str:
        return textwrap.dedent(
            """
            Commands (examples):
            - help
            - status
            - paths
            - collect 50          (runs CLI collect --samples 50)
            - train
            - detect 30
            - anomalies 20
            - explain last
            - explain row 3
            - open logs
            - open parquet
            - open model
            - clear
            """
        ).strip()

    def handle(self, text: str, df_cache: pd.DataFrame) -> ChatReply:
        t = text.strip().lower()

        if t in {"help", "?", "commands"}:
            return ChatReply("Help", self.help_text())

        if t in {"status", "health"}:
            pq = Path(config.parquet_file)
            db = Path(config.sqlite_file)
            model = Path(config.model_file)
            lines = [
                f"UTC now: {now_utc_iso()}",
                f"Parquet: {'OK' if pq.exists() else 'missing'}  ({pq})",
                f"SQLite:  {'OK' if db.exists() else 'missing'}  ({db})",
                f"Model:   {'OK' if model.exists() else 'missing'} ({model})",
                f"Rows loaded (cache): {len(df_cache)}",
            ]
            return ChatReply("System Status", "\n".join(lines))

        if t == "paths":
            return ChatReply(
                "Paths",
                "\n".join(
                    [
                        f"project_root: {project_root()}",
                        f"parquet_file: {config.parquet_file}",
                        f"sqlite_file:  {config.sqlite_file}",
                        f"model_file:   {config.model_file}",
                        f"log_file:    {config.log_file}",
                    ]
                ),
            )

        m = re.match(r"^collect\s+(\d+)$", t)
        if m:
            n = int(m.group(1))
            p = run_cmd_in_project([sys.executable, "-m", "sba.cli.app", "collect", "--samples", str(n)])
            out = (p.stdout or "").strip()
            err = (p.stderr or "").strip()
            return ChatReply(
                f"Collect {n}",
                (out if out else "(no stdout)") + ("\n\n[stderr]\n" + err if err else ""),
            )

        if t == "train":
            try:
                train_isolation_forest(Path(config.parquet_file), Path(config.model_file))
                return ChatReply("Train", f"✅ Model trained and saved to:\n{config.model_file}")
            except Exception as e:
                return ChatReply("Train (error)", str(e))

        m = re.match(r"^detect\s+(\d+)$", t)
        if m:
            limit = int(m.group(1))
            try:
                df = detect_anomalies(Path(config.parquet_file), Path(config.model_file))
                anom = df[df.get("is_anomaly", False) == True] if "is_anomaly" in df.columns else pd.DataFrame()
                show = anom.tail(limit) if not anom.empty else pd.DataFrame()
                return ChatReply(
                    "Detect",
                    f"Anomalies total: {int(df['is_anomaly'].sum()) if 'is_anomaly' in df.columns else 0}\n\n"
                    + (show.to_string(index=False) if not show.empty else "No anomalies to show."),
                )
            except Exception as e:
                return ChatReply("Detect (error)", str(e))

        m = re.match(r"^anomalies\s+(\d+)$", t)
        if m:
            limit = int(m.group(1))
            if df_cache.empty:
                return ChatReply("Anomalies", "No data loaded yet.")
            if "is_anomaly" not in df_cache.columns:
                return ChatReply("Anomalies", "No is_anomaly column in current table. Run Detect first.")
            anom = df_cache[df_cache["is_anomaly"] == True].tail(limit)
            return ChatReply("Anomalies", anom.to_string(index=False) if not anom.empty else "None in the loaded window.")

        if t == "explain last":
            if df_cache.empty:
                return ChatReply("Explain", "No data loaded.")
            row = df_cache.tail(1).iloc[0]
            return ChatReply("Explain last row", self._explain_row(row))

        m = re.match(r"^explain\s+row\s+(\d+)$", t)
        if m:
            idx = int(m.group(1))
            if df_cache.empty:
                return ChatReply("Explain", "No data loaded.")
            if idx < 0 or idx >= len(df_cache):
                return ChatReply("Explain", f"Row out of range. 0..{len(df_cache)-1}")
            row = df_cache.iloc[idx]
            return ChatReply(f"Explain row {idx}", self._explain_row(row))

        if t == "open logs":
            return ChatReply("Open logs", str(config.log_file))

        if t == "open parquet":
            return ChatReply("Open parquet", str(config.parquet_file))

        if t == "open model":
            return ChatReply("Open model", str(config.model_file))

        if t == "clear":
            return ChatReply("Clear", "__CLEAR__")

        return ChatReply("Unknown command", "Type `help` to see what I can do.")

    def _explain_row(self, row: pd.Series) -> str:
        cpu = float(row.get("cpu_percent", 0.0))
        mem = float(row.get("mem_percent", 0.0))
        disk = float(row.get("disk_percent", 0.0))
        sent = float(row.get("net_sent_kb_s", 0.0))
        recv = float(row.get("net_recv_kb_s", 0.0))
        is_anom = bool(row.get("is_anomaly", False))
        score = row.get("anomaly_score", None)

        reasons = []
        if cpu >= 80:
            reasons.append("CPU is very high (>=80%).")
        if mem >= 85:
            reasons.append("RAM is very high (>=85%).")
        if disk >= 90:
            reasons.append("Disk usage is very high (>=90%).")
        if recv >= 800 or sent >= 800:
            reasons.append("Network spike (>=800 KB/s).")
        if not reasons:
            reasons.append("No extreme metric spikes found; anomaly may be multi-factor / rare pattern.")

        return "\n".join(
            [
                f"ts_utc: {row.get('ts_utc', '-')}",
                f"is_anomaly: {is_anom}",
                f"anomaly_score: {score}",
                "",
                "Quick read:",
                f"- CPU:  {cpu:.1f}%",
                f"- RAM:  {mem:.1f}%",
                f"- Disk: {disk:.1f}%",
                f"- Net:  sent={sent:.1f} KB/s  recv={recv:.1f} KB/s",
                "",
                "Why (simple explanation):",
                *[f"- {r}" for r in reasons],
                "",
                "Tip:",
                "- Collect more samples (collect 200), train again, then detect again for better results.",
            ]
        )


# ---------------------------
# Main Window
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("System Behavior Analyzer — Pro")
        self.resize(1200, 720)

        self.assistant = LocalAssistant()
        self.df_current = pd.DataFrame()

        # Central layout
        root = QWidget()
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(14, 14, 14, 14)
        self.sidebar.setLayout(sb_layout)

        title = QLabel("SBA Pro")
        title.setObjectName("Title")
        subtitle = QLabel("Live Monitoring • Anomalies • Automation")
        subtitle.setObjectName("Subtitle")

        sb_layout.addWidget(title)
        sb_layout.addWidget(subtitle)

        sb_layout.addSpacing(12)

        self.nav = QListWidget()
        self.nav.setSpacing(4)
        for name in ["Dashboard", "Anomalies", "AI Chat", "Settings"]:
            item = QListWidgetItem(name)
            self.nav.addItem(item)
        self.nav.setCurrentRow(0)
        sb_layout.addWidget(self.nav, 1)

        sb_layout.addSpacing(10)

        self.btn_collect = QPushButton("Collect 50")
        self.btn_collect.setObjectName("Primary")
        self.btn_train = QPushButton("Train Model")
        self.btn_detect = QPushButton("Detect Now")
        self.btn_detect.setObjectName("Primary")

        sb_layout.addWidget(self.btn_collect)
        sb_layout.addWidget(self.btn_train)
        sb_layout.addWidget(self.btn_detect)

        sb_layout.addSpacing(10)

        self.live_check = QCheckBox("Live refresh")
        self.live_check.setChecked(True)
        sb_layout.addWidget(self.live_check)

        self.status = QLabel("Ready.")
        self.status.setObjectName("Subtitle")
        sb_layout.addWidget(self.status)

        # Main area
        main = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main.setLayout(main_layout)

        # Topbar
        topbar = QFrame()
        topbar.setObjectName("Topbar")
        topbar_layout = QHBoxLayout()
        topbar_layout.setContentsMargins(0, 0, 0, 10)
        topbar.setLayout(topbar_layout)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Quick command… e.g. detect 30, collect 200, help")
        self.search.returnPressed.connect(self.quick_command)

        self.btn_run = QPushButton("Run")
        self.btn_run.setObjectName("Primary")
        self.btn_run.clicked.connect(self.quick_command)

        topbar_layout.addWidget(self.search, 1)
        topbar_layout.addWidget(self.btn_run)

        main_layout.addWidget(topbar)

        # Pages
        self.pages = QStackedWidget()
        main_layout.addWidget(self.pages, 1)

        self.page_dashboard = self._build_dashboard()
        self.page_anomalies = self._build_anomalies()
        self.page_chat = self._build_chat()
        self.page_settings = self._build_settings()

        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_anomalies)
        self.pages.addWidget(self.page_chat)
        self.pages.addWidget(self.page_settings)

        # Splitter: sidebar | main
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(main)
        splitter.setSizes([260, 940])
        root_layout.addWidget(splitter)

        # Signals
        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.btn_collect.clicked.connect(lambda: self.run_collect(50))
        self.btn_train.clicked.connect(self.run_train)
        self.btn_detect.clicked.connect(self.run_detect)

        # Timer for live refresh
        self.timer = QTimer(self)
        self.timer.setInterval(1500)  # ms
        self.timer.timeout.connect(self.refresh_live)
        self.timer.start()

        # Menu
        self._build_menu()

        # initial load
        self.refresh_all()

    def _build_menu(self) -> None:
        m = self.menuBar()
        file_menu = m.addMenu("File")

        act_refresh = QAction("Refresh now", self)
        act_refresh.triggered.connect(self.refresh_all)
        file_menu.addAction(act_refresh)

        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        tools_menu = m.addMenu("Tools")
        act_train = QAction("Train model", self)
        act_train.triggered.connect(self.run_train)
        tools_menu.addAction(act_train)

        act_detect = QAction("Detect anomalies", self)
        act_detect.triggered.connect(self.run_detect)
        tools_menu.addAction(act_detect)

    def _card(self, big: str, small: str) -> QFrame:
        c = QFrame()
        c.setObjectName("Card")
        lay = QVBoxLayout()
        lay.setContentsMargins(14, 12, 14, 12)
        c.setLayout(lay)

        a = QLabel(big)
        a.setObjectName("CardBig")
        b = QLabel(small)
        b.setObjectName("CardSmall")
        lay.addWidget(a)
        lay.addWidget(b)
        return c

    def _build_dashboard(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        w.setLayout(layout)

        # KPI cards
        kpi = QWidget()
        grid = QGridLayout()
        grid.setSpacing(12)
        kpi.setLayout(grid)

        self.card_rows = self._card("-", "rows in parquet")
        self.card_anom = self._card("-", "anomalies total (last detect)")
        self.card_last = self._card("-", "last timestamp")

        grid.addWidget(self.card_rows, 0, 0)
        grid.addWidget(self.card_anom, 0, 1)
        grid.addWidget(self.card_last, 0, 2)

        layout.addWidget(kpi)

        # Charts
        charts = QWidget()
        cg = QGridLayout()
        cg.setSpacing(12)
        charts.setLayout(cg)

        self.ch_cpu = MetricChart("CPU %")
        self.ch_mem = MetricChart("RAM %")
        self.ch_net = MetricChart("Network recv KB/s")
        self.ch_disk = MetricChart("Disk %")

        cg.addWidget(self._wrap_chart(self.ch_cpu), 0, 0)
        cg.addWidget(self._wrap_chart(self.ch_mem), 0, 1)
        cg.addWidget(self._wrap_chart(self.ch_net), 1, 0)
        cg.addWidget(self._wrap_chart(self.ch_disk), 1, 1)

        layout.addWidget(charts, 1)

        return w

    def _wrap_chart(self, chart: MetricChart) -> QFrame:
        c = QFrame()
        c.setObjectName("Card")
        lay = QVBoxLayout()
        lay.setContentsMargins(12, 10, 12, 10)
        c.setLayout(lay)
        lay.addWidget(chart)
        return c

    def _build_anomalies(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        w.setLayout(layout)

        top = QHBoxLayout()
        self.anom_limit = QSpinBox()
        self.anom_limit.setRange(10, 5000)
        self.anom_limit.setValue(50)

        self.only_anom = QCheckBox("Show only anomalies")
        self.only_anom.setChecked(True)

        self.btn_refresh_table = QPushButton("Refresh Table")
        self.btn_refresh_table.clicked.connect(self.refresh_table)

        top.addWidget(QLabel("Rows:"))
        top.addWidget(self.anom_limit)
        top.addSpacing(12)
        top.addWidget(self.only_anom)
        top.addStretch(1)
        top.addWidget(self.btn_refresh_table)

        layout.addLayout(top)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 1)

        return w

    def _build_chat(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        w.setLayout(layout)

        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setFont(QFont("Consolas", 10))

        row = QHBoxLayout()
        self.chat_in = QLineEdit()
        self.chat_in.setPlaceholderText("Talk to SBA… try: help, status, collect 200, train, detect 30, explain last")
        self.chat_in.returnPressed.connect(self.send_chat)

        btn = QPushButton("Send")
        btn.setObjectName("Primary")
        btn.clicked.connect(self.send_chat)

        row.addWidget(self.chat_in, 1)
        row.addWidget(btn)

        layout.addWidget(self.chat_view, 1)
        layout.addLayout(row)

        self._chat_append("SBA", "Yo 👋 I’m your local assistant. Type `help` to see commands.")
        return w

    def _build_settings(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        w.setLayout(layout)

        card = QFrame()
        card.setObjectName("Card")
        lay = QVBoxLayout()
        lay.setContentsMargins(14, 12, 14, 12)
        card.setLayout(lay)

        lay.addWidget(QLabel("Settings (simple)"))
        lay.addWidget(QLabel(f"Parquet: {config.parquet_file}"))
        lay.addWidget(QLabel(f"SQLite:  {config.sqlite_file}"))
        lay.addWidget(QLabel(f"Model:   {config.model_file}"))
        lay.addWidget(QLabel(f"Logs:    {config.log_file}"))

        layout.addWidget(card)
        layout.addStretch(1)
        return w

    # ---------------------------
    # Actions
    # ---------------------------
    def refresh_live(self) -> None:
        if self.live_check.isChecked():
            self.refresh_all()

    def refresh_all(self) -> None:
        df = safe_read_parquet(Path(config.parquet_file))
        if df.empty:
            self.status.setText("No parquet yet. Run Collect first.")
            self.df_current = pd.DataFrame()
            return

        # basic ordering
        if "ts_utc" in df.columns:
            df = df.sort_values("ts_utc")

        self.df_current = df

        # update cards + charts from last 120 rows
        view = df.tail(120)

        self._set_card(self.card_rows, str(len(df)))
        if "is_anomaly" in df.columns:
            self._set_card(self.card_anom, str(int(df["is_anomaly"].sum())))
        else:
            self._set_card(self.card_anom, "-")

        last_ts = str(view["ts_utc"].iloc[-1]) if "ts_utc" in view.columns and not view.empty else "-"
        self._set_card(self.card_last, last_ts)

        # charts
        if "ts_utc" in view.columns:
            self.ch_cpu.plot(view, "ts_utc", "cpu_percent" if "cpu_percent" in view.columns else view.columns[0])
            if "mem_percent" in view.columns:
                self.ch_mem.plot(view, "ts_utc", "mem_percent")
            if "net_recv_kb_s" in view.columns:
                self.ch_net.plot(view, "ts_utc", "net_recv_kb_s")
            if "disk_percent" in view.columns:
                self.ch_disk.plot(view, "ts_utc", "disk_percent")

        # keep table fresh if anomalies page open
        if self.pages.currentWidget() == self.page_anomalies:
            self.refresh_table()

        self.status.setText(f"Live updated: {now_utc_iso()}")

    def refresh_table(self) -> None:
        df = self.df_current.copy()
        if df.empty:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        n = int(self.anom_limit.value())
        df = df.tail(n)

        if self.only_anom.isChecked() and "is_anomaly" in df.columns:
            df = df[df["is_anomaly"] == True]

        self._fill_table(df)

    def _fill_table(self, df: pd.DataFrame) -> None:
        self.table.clear()
        self.table.setColumnCount(len(df.columns))
        self.table.setRowCount(len(df))
        self.table.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for r in range(len(df)):
            is_anom = False
            if "is_anomaly" in df.columns:
                try:
                    is_anom = bool(df.iloc[r]["is_anomaly"])
                except Exception:
                    is_anom = False

            for c, col in enumerate(df.columns):
                item = QTableWidgetItem(str(df.iloc[r][col]))
                if is_anom:
                    item.setBackground(Qt.darkRed)
                self.table.setItem(r, c, item)

        self.table.resizeColumnsToContents()

    def run_collect(self, n: int) -> None:
        self.status.setText(f"Collecting {n} samples…")
        try:
            p = run_cmd_in_project([sys.executable, "-m", "sba.cli.app", "collect", "--samples", str(n)])
            out = (p.stdout or "").strip()
            err = (p.stderr or "").strip()
            if p.returncode != 0:
                raise RuntimeError(err or out or "collect failed")
            self._chat_append("SBA", f"✅ Collect done.\n{out if out else ''}".strip())
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Collect error", str(e))
            self.status.setText("Collect failed.")

    def run_train(self) -> None:
        self.status.setText("Training model…")
        try:
            train_isolation_forest(Path(config.parquet_file), Path(config.model_file))
            self._chat_append("SBA", f"✅ Model trained:\n{config.model_file}")
            self.status.setText("Train done.")
        except Exception as e:
            QMessageBox.critical(self, "Train error", str(e))
            self.status.setText("Train failed.")

    def run_detect(self) -> None:
        self.status.setText("Detecting anomalies…")
        try:
            df = detect_anomalies(Path(config.parquet_file), Path(config.model_file))
            self.df_current = df
            self._chat_append("SBA", f"✅ Detect done. anomalies: {int(df['is_anomaly'].sum()) if 'is_anomaly' in df.columns else 0}")
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Detect error", str(e))
            self.status.setText("Detect failed.")

    def quick_command(self) -> None:
        cmd = self.search.text().strip()
        if not cmd:
            return
        self.search.clear()
        self._chat_append("You", cmd)
        rep = self.assistant.handle(cmd, self.df_current)

        if rep.body == "__CLEAR__":
            self.chat_view.clear()
            self._chat_append("SBA", "Cleared.")
            return

        self._chat_append(rep.title, rep.body)
        # smart refresh after actions
        if cmd.lower().startswith(("collect", "train", "detect")):
            self.refresh_all()

    def send_chat(self) -> None:
        cmd = self.chat_in.text().strip()
        if not cmd:
            return
        self.chat_in.clear()
        self._chat_append("You", cmd)
        rep = self.assistant.handle(cmd, self.df_current)

        if rep.body == "__CLEAR__":
            self.chat_view.clear()
            self._chat_append("SBA", "Cleared.")
            return

        self._chat_append(rep.title, rep.body)
        if cmd.lower().startswith(("collect", "train", "detect")):
            self.refresh_all()

    def _chat_append(self, who: str, msg: str) -> None:
        self.chat_view.append(f"\n[{who}]")
        self.chat_view.append(msg)

    def _set_card(self, card: QFrame, big: str) -> None:
        # first child label with CardBig
        labels = card.findChildren(QLabel)
        for lab in labels:
            if lab.objectName() == "CardBig":
                lab.setText(big)
                return


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
