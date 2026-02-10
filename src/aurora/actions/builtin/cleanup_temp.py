from aurora.actions.builtin._simulated import SimulatedAction
from aurora.domain.risk import RiskLevel


class CleanupTempAction(SimulatedAction):
    def __init__(self) -> None:
        super().__init__("cleanup_temp", "Cleanup temp files", RiskLevel.LOW, ["Delete temporary files in user temp directories"])
