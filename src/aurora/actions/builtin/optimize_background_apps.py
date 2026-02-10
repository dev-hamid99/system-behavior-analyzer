from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class OptimizeBackgroundAppsAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("optimize_background_apps", "Optimize background apps", RiskLevel.MEDIUM, ["Suspend selected background apps"])
