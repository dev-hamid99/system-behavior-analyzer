from __future__ import annotations

import typer

from aurora.cli.commands import fix, gui, profile, report, scan

app = typer.Typer(help="AURORA CLI")
scan.register(app)
fix.register(app)
profile.register(app)
report.register(app)
gui.register(app)


@app.command("version")
def version() -> None:
    typer.echo("AURORA 0.2.0")


def main() -> None:
    app()
