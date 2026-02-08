"""Entry-point for `python -m sba`.

This simply forwards to the Typer CLI.
"""

from __future__ import annotations

from sba.cli.app import main


if __name__ == "__main__":
    main()
