from __future__ import annotations

import typer
from rich import print

from aurora.advisors.rules_engine import RulesEngine
from aurora.scanners.system_scanner import SystemScanner


def run() -> None:
    result = SystemScanner().scan()
    recs = RulesEngine().recommend(result)
    print({"metrics": result.metrics, "issue_count": len(result.issues), "recommendations": recs})


def register(app: typer.Typer) -> None:
    app.command("scan")(run)
