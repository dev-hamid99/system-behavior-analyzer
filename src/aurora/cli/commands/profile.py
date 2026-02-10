from __future__ import annotations

import typer
from rich import print

from aurora.advisors.presets import SAFE_PRESETS


def list_profiles() -> None:
    print(list(SAFE_PRESETS.keys()))


def register(app: typer.Typer) -> None:
    app.command("profile-list")(list_profiles)
