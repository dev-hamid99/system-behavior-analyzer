from __future__ import annotations

import aurora


def test_aurora_importable() -> None:
    assert aurora.__version__.startswith("0.2")
