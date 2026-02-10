from __future__ import annotations

from aurora.domain.models import ScanResult


class RulesEngine:
    def recommend(self, result: ScanResult) -> list[str]:
        recs: list[str] = []
        for issue in result.issues:
            if issue.code == "cpu_high":
                recs.append("Run repair workflow: Fix high CPU")
            elif issue.code == "ram_high":
                recs.append("Use Booster: optimize background apps")
            elif issue.code == "disk_high":
                recs.append("Run cleanup temp files action")
        if not recs:
            recs.append("System looks healthy. Continue monitoring.")
        return recs
