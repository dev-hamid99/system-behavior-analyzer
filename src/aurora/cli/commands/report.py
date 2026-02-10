from __future__ import annotations

import typer
from rich import print

from aurora.storage.repositories import sqlite_repo


def report() -> None:
    db = sqlite_repo()
    print({"audit_events": db.count_audit()})


def register(app: typer.Typer) -> None:
    app.command("report")(report)
