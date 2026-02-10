from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from aurora.core.constants import LOG_FILENAME
from aurora.core.paths import logs_dir


def setup_logging() -> None:
    log_path = logs_dir() / LOG_FILENAME
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    fh = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    root.addHandler(sh)
