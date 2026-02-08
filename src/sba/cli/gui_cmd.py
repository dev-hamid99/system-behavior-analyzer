from __future__ import annotations

import typer


def gui() -> None:
    """Start the SBA GUI (Guardian)."""
    # Import inside so CLI still works if GUI deps aren't installed
    from sba.guardian_gui.app import main as gui_main

    gui_main()
