from __future__ import annotations

import sys


def main() -> None:
    # `python -m aurora` => GUI
    # `python -m aurora --help` or any args => CLI
    if len(sys.argv) == 1:
        from aurora.gui.app import main as gui_main

        gui_main()
        return

    from aurora.cli.app import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
