from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class CreateRestorePointAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("create_restore_point", "Create restore point", RiskLevel.LOW, ["Trigger Windows restore point creation"])
