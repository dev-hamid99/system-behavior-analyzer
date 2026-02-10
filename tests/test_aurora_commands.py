from __future__ import annotations

from typer.testing import CliRunner

from aurora.cli.app import app


def test_aurora_scan_fix_report_commands() -> None:
    runner = CliRunner()

    r_scan = runner.invoke(app, ["scan"])
    assert r_scan.exit_code == 0

    r_fix = runner.invoke(app, ["fix-preview"])
    assert r_fix.exit_code == 0

    r_report = runner.invoke(app, ["report"])
    assert r_report.exit_code == 0


def test_aurora_gui_command_symbolic(monkeypatch) -> None:
    from aurora.cli.commands import gui as gui_cmd

    monkeypatch.setattr(gui_cmd, "run_gui", lambda: 0)

    runner = CliRunner()
    result = runner.invoke(app, ["gui"])
    assert result.exit_code == 0
