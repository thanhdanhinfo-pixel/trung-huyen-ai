from __future__ import annotations

from agent_orchestrator import AgentOrchestrator
from kernel.kernel import kernel
from kernel.registry import load_registry


class AIWorker:
    """
    One execution tick of AI OS.
    Không chạy while True.
    Mỗi lần gọi tick() là xử lý một chu kỳ.
    """

    def __init__(self):
        self.registry = load_registry()
        self.kernel = kernel
        self.orchestrator = AgentOrchestrator()

    def boot(self):
        return {
            "kernel": self.kernel.boot_status(),
            "registry": self.registry.validate(),
            "status": "ready"
        }

    def tick(self):
        """
        Một chu kỳ làm việc.
        """
        return {
            "boot": self.boot(),
            "workflow": self.orchestrator.run_workflow([]),
            "status": "idle"
        }

    def run_once(self):
        return self.tick()


worker = AIWorker()
