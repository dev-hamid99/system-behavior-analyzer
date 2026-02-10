from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class RunDismAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("run_dism", "Run DISM", RiskLevel.MEDIUM, ["Execute DISM health restore workflow"])
