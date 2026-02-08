from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS metrics (
    ts_utc TEXT PRIMARY KEY,
    cpu_percent REAL,
    mem_percent REAL,
    mem_used_mb REAL,
    disk_percent REAL,
    net_sent_kb_s REAL,
    net_recv_kb_s REAL
);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute(DDL)
        con.commit()


def insert_metric(db_path: Path, row: dict) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            INSERT OR REPLACE INTO metrics
            (ts_utc, cpu_percent, mem_percent, mem_used_mb, disk_percent, net_sent_kb_s, net_recv_kb_s)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["ts_utc"],
                row["cpu_percent"],
                row["mem_percent"],
                row["mem_used_mb"],
                row["disk_percent"],
                row["net_sent_kb_s"],
                row["net_recv_kb_s"],
            ),
        )
        con.commit()
