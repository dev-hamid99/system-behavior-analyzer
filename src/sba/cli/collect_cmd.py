from __future__ import annotations

import logging
import time

from sba.config import config
from sba.logging_config import setup_logging
from sba.collectors.system_metrics import collect_once, metrics_to_dict
from sba.storage.parquet_store import append_metrics_parquet
from sba.storage.sqlite_store import insert_metric

log = logging.getLogger("sba.collect")


def run_collect(samples: int | None = None) -> None:
    setup_logging(config.logs_dir)
    log.info(
        "Starting collection: interval=%ss samples=%s",
        config.sample_interval_sec,
        samples,
    )

    prev_net = None
    i = 0

    while True:
        start = time.time()

        metrics, prev_net = collect_once(prev_net, config.sample_interval_sec)
        row = metrics_to_dict(metrics)

        append_metrics_parquet(config.parquet_file, row)
        insert_metric(config.sqlite_file, row)

        log.info("Collected: %s", row)

        i += 1
        if samples is not None and i >= samples:
            break

        elapsed = time.time() - start
        time.sleep(max(config.sample_interval_sec - elapsed, 0.0))
