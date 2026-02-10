from __future__ import annotations

from aurora.ai.memory_store import MemoryStore
from aurora.ai.safety import SAFE_GUARD_MESSAGE
from aurora.ai.tools import run_quick_scan


class ChatEngine:
    def __init__(self, memory: MemoryStore | None = None) -> None:
        self.memory = memory or MemoryStore()

    def generate_response(self, message: str, context: str = "") -> str:
        text = message.lower().strip()
        self.memory.add(message)
        if "quick scan" in text or "scan" in text:
            data = run_quick_scan()
            return (
                f"Quick scan complete. Issues: {len(data['issues'])}. "
                f"Top recommendation: {data['recommendations'][0]}. {SAFE_GUARD_MESSAGE}"
            )
        if "slow" in text or "cpu" in text:
            return "I suggest running 'Fix high CPU' workflow with preview, risk, and rollback first. " + SAFE_GUARD_MESSAGE
        return "I can run guided diagnostics, explain findings, and prepare a fix plan. " + SAFE_GUARD_MESSAGE
