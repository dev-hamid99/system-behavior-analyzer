from __future__ import annotations

from aurora.ai.tools import run_quick_scan


def test_quick_scan_returns_structure() -> None:
    data = run_quick_scan()
    assert "metrics" in data
    assert "issues" in data
    assert "recommendations" in data
