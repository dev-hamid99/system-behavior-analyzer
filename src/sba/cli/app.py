from __future__ import annotations

import typer

from sba.cli.collect_cmd import run_collect
from sba.cli.ml_cmd import detect as detect_cmd
from sba.cli.ml_cmd import train as train_cmd

app = typer.Typer(help="System Behavior Analyzer & Automation Engine")


@app.command()
def collect(samples: int = typer.Option(None, help="Number of samples to collect (default: infinite).")) -> None:
    run_collect(samples=samples)


@app.command()
def train() -> None:
    train_cmd()


@app.command()
def detect(limit: int = typer.Option(20, help="Show last N anomalies.")) -> None:
    detect_cmd(limit=limit)


@app.command()
def gui() -> None:
    """Launch Guardian GUI (requires optional gui dependencies)."""
    try:
        from sba.guardian_gui.app import run_gui
    except ImportError as exc:  # pragma: no cover - environment-dependent
        typer.echo(
            "GUI dependencies are missing. Install with: python -m pip install -e \".[gui]\"",
            err=True,
        )
        raise typer.Exit(code=1) from exc
    raise SystemExit(run_gui())


def main() -> None:
    app()


if __name__ == "__main__":
    main()
