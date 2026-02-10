from __future__ import annotations

import typer

from aurora.gui.app import run_gui


def launch() -> None:
    run_gui()


def register(app: typer.Typer) -> None:
    app.command("gui")(launch)
