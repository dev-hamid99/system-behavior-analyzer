from __future__ import annotations

import typer
from rich import print

from aurora.actions.builtin.cleanup_temp import CleanupTempAction


def preview() -> None:
    print(CleanupTempAction().preview())


def register(app: typer.Typer) -> None:
    app.command("fix-preview")(preview)
