from __future__ import annotations

import sys

import typer

from aurora.cli.commands import fix, profile, report, scan

app = typer.Typer(help="AURORA CLI")
scan.register(app)
fix.register(app)
profile.register(app)
report.register(app)


@app.command("version")
def version() -> None:
    typer.echo("AURORA 0.2.0")


def main() -> None:
    if len(sys.argv) == 1:
        # default entry: show CLI help for non-GUI environments
        sys.argv.append("--help")
    app()
