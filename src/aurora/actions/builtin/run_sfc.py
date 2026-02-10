from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class RunSfcAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("run_sfc", "Run SFC", RiskLevel.MEDIUM, ["Execute sfc /scannow"])
