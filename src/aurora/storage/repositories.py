from __future__ import annotations

from aurora.core.constants import DB_FILENAME
from aurora.core.paths import data_dir
from aurora.storage.sqlite import SQLiteStore


def sqlite_repo() -> SQLiteStore:
    store = SQLiteStore(data_dir() / DB_FILENAME)
    store.init_db()
    return store
