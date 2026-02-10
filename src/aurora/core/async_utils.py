from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

_EXECUTOR = ThreadPoolExecutor(max_workers=4)


def run_in_worker(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Future[Any]:
    return _EXECUTOR.submit(func, *args, **kwargs)
