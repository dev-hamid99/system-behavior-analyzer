from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class NetworkResetAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("network_reset", "Reset network stack", RiskLevel.HIGH, ["Reset winsock and networking interfaces"])
