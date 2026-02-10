from __future__ import annotations

from pathlib import Path

from aurora.storage.sqlite import SQLiteStore


def test_sqlite_store_works(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "test.db")
    store.init_db()
    store.add_audit("test", "hello")
    assert store.count_audit() == 1
