from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class DisableStartupAppAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("disable_startup_app", "Disable startup app", RiskLevel.LOW, ["Disable selected startup entry"])
