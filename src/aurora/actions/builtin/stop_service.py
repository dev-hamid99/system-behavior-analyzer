from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class StopServiceAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("stop_service", "Stop safe service", RiskLevel.MEDIUM, ["Stop whitelisted non-essential service"])
