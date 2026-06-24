from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent_orchestrator import AgentOrchestrator
from kernel.kernel import kernel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIWorker:
    """AI Worker runtime tick.

    Worker is now migrating to Kernel-first architecture.
    It no longer owns Registry or Health state. Those belong to AIKernel.
    """

    def __init__(self):
        self.kernel = kernel
        self.orchestrator = AgentOrchestrator()
        self.booted = False
        self.booted_at: Optional[str] = None
        self.last_tick: Optional[Dict[str, Any]] = None

    def boot(self) -> Dict[str, Any]:
        if not self.booted:
            self.booted = True
            self.booted_at = _now()

        return {
            "status": "ready",
            "booted": self.booted,
            "booted_at": self.booted_at,
            "kernel": self.kernel.boot_status(),
        }

    def tick(self, tasks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Run one worker cycle.

        In this migration phase, tasks may still be passed in directly.
        The next migration step will move task retrieval to kernel.runtime.queue.
        """
        tick_state = self.kernel.runtime.begin_tick()
        boot_state = self.boot()
        health = self.kernel.health.check(self.kernel)

        if health.get("status") != "ok":
            result = {
                "status": "blocked",
                "boot": boot_state,
                "health": health,
                "workflow": None,
            }
            ended = self.kernel.runtime.end_tick(tick_state, status="blocked", result=result)
            self.last_tick = ended.as_dict()
            return self.last_tick

        if not tasks:
            result = {
                "status": "idle",
                "boot": boot_state,
                "health": health,
                "workflow": {
                    "status": "idle",
                    "message": "No tasks supplied for this tick. Queue migration is next.",
                },
            }
            ended = self.kernel.runtime.end_tick(tick_state, status="idle", result=result)
            self.last_tick = ended.as_dict()
            return self.last_tick

        action_validation = self.kernel.validate_action({
            "type": "execute_plan",
            "target": "worker.tick.tasks",
            "approved": True,
        })
        if action_validation.get("status") == "blocked":
            result = {
                "status": "blocked",
                "boot": boot_state,
                "health": health,
                "governance": action_validation,
                "workflow": None,
            }
            ended = self.kernel.runtime.end_tick(tick_state, status="blocked", result=result)
            self.last_tick = ended.as_dict()
            return self.last_tick

        workflow = self.orchestrator.run_workflow(tasks)
        result = {
            "status": workflow.get("status", "ok"),
            "boot": boot_state,
            "health": health,
            "governance": action_validation,
            "workflow": workflow,
        }
        ended = self.kernel.runtime.end_tick(
            tick_state,
            status=result.get("status", "ok"),
            result=result,
        )
        self.last_tick = ended.as_dict()
        return self.last_tick

    def run_once(self, tasks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self.tick(tasks=tasks)

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "booted": self.booted,
            "booted_at": self.booted_at,
            "kernel_runtime": self.kernel.runtime.snapshot(),
            "last_tick": self.last_tick,
        }


worker = AIWorker()
