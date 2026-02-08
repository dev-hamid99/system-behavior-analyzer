from __future__ import annotations

import typer

from sba.cli.collect_cmd import run_collect
from sba.cli.ml_cmd import train as train_cmd, detect as detect_cmd

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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
