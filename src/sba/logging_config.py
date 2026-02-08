from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sba.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # verhindert doppelte Handler (z.B. bei wiederholtem setup_logging in Tests)
    if logger.handlers:
        return

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,  # ~5MB
        backupCount=3,
        encoding="utf-8",
    )
    stream_handler = logging.StreamHandler()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    file_handler.setFormatter(fmt)
    stream_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
