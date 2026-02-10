from __future__ import annotations

from typer.testing import CliRunner

from aurora.cli.app import app


def test_aurora_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AURORA CLI" in result.stdout
