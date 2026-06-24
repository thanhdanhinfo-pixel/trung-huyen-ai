from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent_orchestrator import AgentOrchestrator
from kernel.kernel import kernel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIWorker:
    """AI Worker runtime tick.

    Worker uses AIKernel as the system state owner. It does not own Registry,
    Runtime, Queue, Health or Governance state.
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

    def _tasks_from_kernel_queue(self, limit: int = 1) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []
        for _ in range(max(limit, 1)):
            task = self.kernel.runtime.queue.pop()
            if not task:
                break
            tasks.append(task.to_dict())
        return tasks

    def tick(self, tasks: Optional[List[Dict[str, Any]]] = None, max_queue_tasks: int = 1) -> Dict[str, Any]:
        """Run one worker cycle.

        If tasks are provided, the worker executes them for compatibility.
        If tasks are omitted, the worker pulls pending tasks from
        kernel.runtime.queue, making Kernel Runtime the queue owner.
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

        source = "provided" if tasks is not None else "kernel.runtime.queue"
        tasks_to_run = tasks if tasks is not None else self._tasks_from_kernel_queue(limit=max_queue_tasks)

        if not tasks_to_run:
            result = {
                "status": "idle",
                "boot": boot_state,
                "health": health,
                "task_source": source,
                "workflow": {
                    "status": "idle",
                    "message": "No pending tasks in Kernel Runtime Queue.",
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
                "task_source": source,
                "governance": action_validation,
                "workflow": None,
            }
            ended = self.kernel.runtime.end_tick(tick_state, status="blocked", result=result)
            self.last_tick = ended.as_dict()
            return self.last_tick

        workflow = self.orchestrator.run_workflow(tasks_to_run)
        result = {
            "status": workflow.get("status", "ok"),
            "boot": boot_state,
            "health": health,
            "task_source": source,
            "task_count": len(tasks_to_run),
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
