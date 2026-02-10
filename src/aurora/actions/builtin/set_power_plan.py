from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class SetPowerPlanAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("set_power_plan", "Set power plan", RiskLevel.LOW, ["Switch active power plan"])
