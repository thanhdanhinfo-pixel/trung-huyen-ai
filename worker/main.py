from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent_orchestrator import AgentOrchestrator
from kernel.kernel import kernel
from kernel.registry import SystemRegistry, load_registry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIWorker:
    """
    One execution tick of AI OS.

    Không chạy while True trong core logic.
    Mỗi lần gọi tick() là xử lý một chu kỳ độc lập.
    Phù hợp Cloud Run, Cloud Scheduler, GitHub Actions hoặc daemon wrapper.
    """

    def __init__(self):
        self.kernel = kernel
        self.registry: Optional[SystemRegistry] = None
        self.orchestrator = AgentOrchestrator()
        self.booted = False
        self.booted_at: Optional[str] = None
        self.tick_count = 0
        self.last_tick: Optional[Dict[str, Any]] = None

    def refresh_registry(self) -> SystemRegistry:
        self.registry = load_registry()
        return self.registry

    def boot(self) -> Dict[str, Any]:
        if not self.booted:
            self.refresh_registry()
            self.booted = True
            self.booted_at = _now()

        return {
            "status": "ready",
            "booted": self.booted,
            "booted_at": self.booted_at,
            "kernel": self.kernel.boot_status(),
            "registry": self.registry.validate() if self.registry else None,
        }

    def health_check(self) -> Dict[str, Any]:
        if not self.registry:
            return {
                "status": "error",
                "code": "REGISTRY_NOT_LOADED",
                "message": "Registry has not been loaded.",
            }

        registry_health = self.registry.validate()
        blocking_issues = [
            issue for issue in registry_health.get("issues", [])
            if issue.get("level") == "error"
        ]

        return {
            "status": "ok" if not blocking_issues else "error",
            "registry": registry_health,
            "blocking_issues": blocking_issues,
        }

    def begin_tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        return {
            "tick": self.tick_count,
            "started_at": _now(),
            "status": "running",
        }

    def end_tick(self, tick_state: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
        tick_state["ended_at"] = _now()
        tick_state["status"] = result.get("status", "unknown")
        tick_state["result"] = result
        self.last_tick = tick_state
        return tick_state

    def tick(self, tasks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Run one worker cycle.

        Args:
            tasks: optional tasks to execute during this tick. If omitted, the
                worker returns idle. Persistent queue integration will be added
                in the next phase.
        """
        tick_state = self.begin_tick()
        boot_state = self.boot()

        # Refresh registry every tick so the Worker does not operate on stale
        # system knowledge.
        self.refresh_registry()
        health = self.health_check()
        if health.get("status") != "ok":
            return self.end_tick(
                tick_state,
                {
                    "status": "blocked",
                    "boot": boot_state,
                    "health": health,
                    "workflow": None,
                },
            )

        if not tasks:
            return self.end_tick(
                tick_state,
                {
                    "status": "idle",
                    "boot": boot_state,
                    "health": health,
                    "workflow": {
                        "status": "idle",
                        "message": "No tasks supplied for this tick.",
                    },
                },
            )

        workflow = self.orchestrator.run_workflow(tasks)
        return self.end_tick(
            tick_state,
            {
                "status": workflow.get("status", "ok"),
                "boot": boot_state,
                "health": health,
                "workflow": workflow,
            },
        )

    def run_once(self, tasks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return self.tick(tasks=tasks)

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "booted": self.booted,
            "booted_at": self.booted_at,
            "tick_count": self.tick_count,
            "last_tick": self.last_tick,
        }


worker = AIWorker()
