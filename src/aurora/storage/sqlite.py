from __future__ import annotations

import sqlite3
from pathlib import Path


class SQLiteStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def init_db(self) -> None:
        with self.connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_audit(self, event_type: str, message: str) -> None:
        with self.connect() as con:
            con.execute("INSERT INTO audit_log(event_type, message) VALUES(?, ?)", (event_type, message))

    def count_audit(self) -> int:
        with self.connect() as con:
            row = con.execute("SELECT COUNT(*) FROM audit_log").fetchone()
        return int(row[0]) if row else 0
