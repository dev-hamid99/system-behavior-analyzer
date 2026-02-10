from __future__ import annotations

import os
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import psutil
from PySide6.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel,
    QObject, QThread, QTimer, Signal, Slot
)
from PySide6.QtGui import QAction, QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox,
    QTableView, QAbstractItemView, QMenu, QMessageBox, QApplication
)


@dataclass(frozen=True)
class ProcRow:
    pid: int
    name: str
    cpu: float      # 0..100 normalized
    ram_mb: float
    status: str
    path: str


# -----------------------------
# Worker (real thread, queued)
# -----------------------------
class ProcWorker(QObject):
    result = Signal(list)  # List[ProcRow]

    def __init__(self) -> None:
        super().__init__()
        self._cache: Dict[int, psutil.Process] = {}
        self._primed_global = False

    @Slot(str, int)
    def scan(self, query: str, limit: int) -> None:
        # interruption-friendly
        try:
            if QThread.currentThread().isInterruptionRequested():
                return
        except Exception:
            pass

        q = (query or "").strip().lower()
        ncpu = psutil.cpu_count(logical=True) or 1

        # prime global cpu_percent once
        if not self._primed_global:
            try:
                psutil.cpu_percent(interval=None)
            except Exception:
                pass
            self._primed_global = True

        # We keep only the top (limit) by CPU, using a heap to avoid sorting everything.
        top: List[ProcRow] = []
        seen: set[int] = set()

        # Iterate once, minimize syscalls. attrs gives cheap info; heavy calls inside oneshot.
        for p in psutil.process_iter(attrs=["pid", "name", "status", "exe"]):
            try:
                info = p.info
                pid = int(info.get("pid") or 0)
                if pid <= 0:
                    continue

                name = str(info.get("name") or "")
                if name.lower() == "system idle process":
                    continue

                status = str(info.get("status") or "")
                exe = str(info.get("exe") or "")
                path = exe or ""

                seen.add(pid)

                # FAST filter (before heavy calls)
                if q:
                    nl = name.lower()
                    pl = path.lower()
                    if q.isdigit():
                        qpid = int(q)
                        if qpid != pid and q not in nl and q not in pl:
                            continue
                    else:
                        if q not in nl and q not in pl:
                            continue

                proc = self._cache.get(pid)
                if proc is None:
                    proc = psutil.Process(pid)
                    self._cache[pid] = proc
                    # per-proc cpu prime
                    try:
                        proc.cpu_percent(interval=None)
                    except Exception:
                        self._cache.pop(pid, None)
                        continue

                # heavy metrics in oneshot (reduces syscalls)
                try:
                    with proc.oneshot():
                        cpu_raw = float(proc.cpu_percent(interval=None))
                        cpu = round(cpu_raw / ncpu, 1)

                        try:
                            rss = proc.memory_info().rss
                            ram_mb = round(float(rss) / (1024.0 * 1024.0), 1)
                        except Exception:
                            ram_mb = 0.0
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self._cache.pop(pid, None)
                    continue
                except Exception:
                    continue

                ui_path = path or name
                row = ProcRow(pid, name, cpu, ram_mb, status, ui_path)

                # Maintain top-N by cpu without sorting whole list
                # heapq.nlargest at end would need all rows; instead keep small buffer:
                top.append(row)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception:
                continue

        # cleanup cache
        if self._cache:
            for pid in list(self._cache.keys()):
                if pid not in seen:
                    self._cache.pop(pid, None)

        # pick top limit (fast)
        if len(top) > limit:
            top = heapq.nlargest(limit, top, key=lambda r: r.cpu)
        else:
            top.sort(key=lambda r: r.cpu, reverse=True)

        self.result.emit(top)


# -----------------------------
# Model (delta updates + stable)
# -----------------------------
class ProcModel(QAbstractTableModel):
    HEADERS = ["Name", "PID", "CPU %", "RAM (MB)", "Status", "Path"]

    def __init__(self) -> None:
        super().__init__()
        self._rows: List[ProcRow] = []
        self._pid_to_row: Dict[int, int] = {}

    @property
    def rows(self) -> List[ProcRow]:
        return self._rows

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        r = self._rows[index.row()]
        c = index.column()

        # numeric + stable sorting role
        if role == Qt.UserRole:
            if c == 0: return r.name.lower()
            if c == 1: return r.pid
            if c == 2: return r.cpu
            if c == 3: return r.ram_mb
            if c == 4: return r.status.lower()
            if c == 5: return r.path.lower()

        if role == Qt.DisplayRole:
            if c == 0: return r.name
            if c == 1: return str(r.pid)
            if c == 2: return f"{r.cpu:.1f}"
            if c == 3: return f"{r.ram_mb:.1f}"
            if c == 4: return r.status
            if c == 5: return r.path

        if role == Qt.TextAlignmentRole:
            if c in (1, 2, 3):
                return int(Qt.AlignRight | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)

        if role == Qt.ToolTipRole:
            return f"{r.name} (PID {r.pid})\n{r.path}"

        return None

    def _rebuild_index(self) -> None:
        self._pid_to_row = {r.pid: i for i, r in enumerate(self._rows)}

    def set_rows_delta(self, new_rows: List[ProcRow]) -> None:
        """
        Delta update strategy:
        - remove vanished pids
        - insert new pids
        - update changed rows in place
        This avoids beginResetModel() and makes UI feel instant.
        """
        old_pids = set(self._pid_to_row.keys())
        new_pids = {r.pid for r in new_rows}

        # 1) removals (from bottom to top to keep indices valid)
        removed = sorted((self._pid_to_row[pid] for pid in old_pids - new_pids), reverse=True)
        for row_idx in removed:
            self.beginRemoveRows(QModelIndex(), row_idx, row_idx)
            self._rows.pop(row_idx)
            self.endRemoveRows()
        if removed:
            self._rebuild_index()

        # 2) inserts (append; sorting handled by proxy)
        inserts = [r for r in new_rows if r.pid not in self._pid_to_row]
        if inserts:
            start = len(self._rows)
            end = start + len(inserts) - 1
            self.beginInsertRows(QModelIndex(), start, end)
            self._rows.extend(inserts)
            self.endInsertRows()
            self._rebuild_index()

        # 3) updates (dataChanged only for changed rows)
        # Build quick lookup for new rows
        new_map = {r.pid: r for r in new_rows}
        for pid, i in self._pid_to_row.items():
            nr = new_map.get(pid)
            if nr is None:
                continue
            if self._rows[i] != nr:
                self._rows[i] = nr
                top_left = self.index(i, 0)
                bottom_right = self.index(i, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole, Qt.UserRole, Qt.ToolTipRole])

    def row_at_proxy(self, proxy_row: int, proxy: QSortFilterProxyModel) -> Optional[ProcRow]:
        src = proxy.mapToSource(proxy.index(proxy_row, 0))
        if not src.isValid():
            return None
        i = src.row()
        if 0 <= i < len(self._rows):
            return self._rows[i]
        return None


class ProcProxy(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.q = ""

    def setQuery(self, q: str) -> None:
        self.q = (q or "").strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self.q:
            return True
        m: ProcModel = self.sourceModel()  # type: ignore[assignment]
        r = m.rows[source_row]
        q = self.q
        if q.isdigit() and int(q) == r.pid:
            return True
        return (q in r.name.lower()) or (q in r.path.lower())


# -----------------------------
# Page (coalesced apply + no scan on typing)
# -----------------------------
class ProcessesPage(QWidget):
    scan_requested = Signal(str, int)

    def __init__(self) -> None:
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Processes")
        title.setObjectName("TitleXL")
        sub = QLabel("Smooth process manager (Task Manager style).")
        sub.setObjectName("Muted")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        header.addLayout(title_box, 1)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter (name / path / pid)…")
        self.search.setMaximumWidth(360)
        header.addWidget(self.search)

        self.chk_auto = QCheckBox("Auto refresh")
        self.chk_auto.setChecked(True)
        header.addWidget(self.chk_auto)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        header.addWidget(self.btn_refresh)

        root.addLayout(header)

        # model/proxy/view
        self.model = ProcModel()
        self.proxy = ProcProxy()
        self.proxy.setSourceModel(self.model)
        self.proxy.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setSortRole(Qt.UserRole)

        self.view = QTableView()
        self.view.setModel(self.proxy)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(True)
        self.view.horizontalHeader().setStretchLastSection(True)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        root.addWidget(self.view, 1)

        self.view.customContextMenuRequested.connect(self._ctx_menu)

        # Worker thread
        self._thread = QThread(self)
        self._worker = ProcWorker()
        self._worker.moveToThread(self._thread)
        self.scan_requested.connect(self._worker.scan, Qt.QueuedConnection)
        self._worker.result.connect(self._on_worker_rows, Qt.QueuedConnection)
        self._thread.start()

        # UI apply coalescing: worker may emit quickly, but we apply at most every ~80ms
        self._pending_rows: Optional[List[ProcRow]] = None
        self._apply_timer = QTimer(self)
        self._apply_timer.setSingleShot(True)
        self._apply_timer.setInterval(80)
        self._apply_timer.timeout.connect(self._apply_pending)

        # Refresh timer
        self._timer = QTimer(self)
        self._timer.setInterval(1800)
        self._timer.timeout.connect(self.refresh)

        # Wiring: search only filters locally -> zero lag while typing
        self.search.textChanged.connect(self.proxy.setQuery)
        self.btn_refresh.clicked.connect(self.refresh)
        self.chk_auto.toggled.connect(self._on_auto)

        self._timer.start()
        self.refresh()

        # widths once
        self.view.setColumnWidth(0, 240)
        self.view.setColumnWidth(1, 90)
        self.view.setColumnWidth(2, 90)
        self.view.setColumnWidth(3, 110)
        self.view.setColumnWidth(4, 110)

    def _on_auto(self, on: bool) -> None:
        if on:
            self._timer.start()
        else:
            self._timer.stop()

    def refresh(self) -> None:
        # Keep scanning using current query so results list stays small when filtered
        q = self.search.text()
        limit = 250
        self.scan_requested.emit(q, limit)

    def _on_worker_rows(self, rows: list) -> None:
        # store latest, coalesce UI apply
        self._pending_rows = list(rows)
        if not self._apply_timer.isActive():
            self._apply_timer.start()

    def _apply_pending(self) -> None:
        rows = self._pending_rows
        self._pending_rows = None
        if rows is None:
            return

        # prevent micro-jitter repaints
        self.view.setUpdatesEnabled(False)
        try:
            self.model.set_rows_delta(rows)
        finally:
            self.view.setUpdatesEnabled(True)

        # keep sort indicator stable (proxy will re-sort)
        self.view.sortByColumn(
            self.view.horizontalHeader().sortIndicatorSection(),
            self.view.horizontalHeader().sortIndicatorOrder()
        )

    def _ctx_menu(self, pos) -> None:
        idx = self.view.indexAt(pos)
        if not idx.isValid():
            return
        row = self.model.row_at_proxy(idx.row(), self.proxy)
        if row is None:
            return

        menu = QMenu(self)

        act_copy = QAction("Copy Path", self)
        act_open = QAction("Open File Location", self)
        act_end = QAction("End Task (Terminate)", self)

        real_path = row.path if row.path and os.path.isabs(row.path) else ""
        act_open.setEnabled(bool(real_path and os.path.exists(real_path)))

        menu.addAction(act_copy)
        menu.addAction(act_open)
        menu.addSeparator()
        menu.addAction(act_end)

        def copy_path():
            try:
                QApplication.clipboard().setText(row.path or "")
            except Exception:
                pass

        def open_location():
            p = real_path
            if not p or not os.path.exists(p):
                return
            try:
                os.startfile(os.path.dirname(p))
            except Exception:
                pass

        def end_task():
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Confirm End Task")
            msg.setText(f"Terminate process?\n\n{row.name} (PID {row.pid})")
            msg.setInformativeText("This can cause data loss.")
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
            msg.setDefaultButton(QMessageBox.Cancel)
            if msg.exec() != QMessageBox.Yes:
                return
            try:
                psutil.Process(row.pid).terminate()
            except Exception as e:
                QMessageBox.critical(self, "Failed", f"Could not terminate PID {row.pid}\n{e}")

        act_copy.triggered.connect(copy_path)
        act_open.triggered.connect(open_location)
        act_end.triggered.connect(end_task)

        menu.exec(QCursor.pos())

    def closeEvent(self, e) -> None:  # type: ignore[override]
        try:
            self._thread.requestInterruption()
            self._thread.quit()
            self._thread.wait(1500)
        except Exception:
            pass
        super().closeEvent(e)
