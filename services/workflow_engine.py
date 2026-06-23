from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

WorkflowStatus = Literal[
    "submitted",
    "waiting_approval",
    "running",
    "done",
    "failed",
    "rejected",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkflowTask:
    id: str
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    status: WorkflowStatus = "submitted"
    requires_approval: bool = False
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def record(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.history.append({"at": utc_now(), "event": event, "data": data or {}})
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkflowEngine:
    """Small workflow runner for TRUNG_HUYEN_AI_OS.

    The engine owns multi-step execution policy. Runtime and API layers submit
    work here; concrete adapters such as DeveloperRuntime do the actual work.
    """

    def __init__(self) -> None:
        self.tasks: List[WorkflowTask] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "engine": "workflow",
            "task_count": len(self.tasks),
            "queue": self.queue_summary(),
        }

    def queue_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {}
        for task in self.tasks:
            summary[task.status] = summary.get(task.status, 0) + 1
        return summary

    def submit(
        self,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        requires_approval: bool = False,
        auto_run: bool = True,
    ) -> Dict[str, Any]:
        task = WorkflowTask(
            id=f"wf-task-{len(self.tasks) + 1:04d}",
            action=action,
            payload=payload or {},
            requires_approval=requires_approval,
        )
        task.record("submitted", {"requires_approval": requires_approval})
        self.tasks.append(task)

        if requires_approval:
            task.status = "waiting_approval"
            task.record("waiting_approval")
            return {"status": task.status, "task": task.to_dict()}

        if auto_run:
            return self.run(task.id)

        return {"status": task.status, "task": task.to_dict()}

    def run(self, task_id: str) -> Dict[str, Any]:
        task = self._find(task_id)
        task.status = "running"
        task.attempts += 1
        task.record("running", {"attempts": task.attempts})

        try:
            result = self._execute_action(task.action, task.payload)
            task.result = result
            task.status = "done" if result.get("status") not in {"error", "failed"} else "failed"
            task.record(task.status, {"result": result})
            return {"status": task.status, "task": task.to_dict(), "result": result}
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error = f"{type(exc).__name__}: {exc}"
            task.record("failed", {"error": task.error})
            return {"status": "failed", "task": task.to_dict(), "error": task.error}

    def approve(self, task_id: str) -> Dict[str, Any]:
        task = self._find(task_id)
        if task.status != "waiting_approval":
            return {"status": "noop", "message": "Task is not waiting for approval", "task": task.to_dict()}
        task.requires_approval = False
        task.record("approved")
        return self.run(task_id)

    def reject(self, task_id: str, reason: str = "") -> Dict[str, Any]:
        task = self._find(task_id)
        task.status = "rejected"
        task.error = reason or "Rejected"
        task.record("rejected", {"reason": task.error})
        return {"status": "rejected", "task": task.to_dict()}

    def retry(self, task_id: str) -> Dict[str, Any]:
        task = self._find(task_id)
        if task.attempts >= task.max_attempts:
            task.status = "failed"
            task.record("retry_exhausted", {"attempts": task.attempts})
            return {"status": "failed", "task": task.to_dict()}
        task.record("retry_requested")
        return self.run(task_id)

    def queue(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.tasks]

    def history(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if task_id:
            return self._find(task_id).history
        return [task.to_dict() for task in self.tasks]

    def _find(self, task_id: str) -> WorkflowTask:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError("Workflow task not found")

    def _execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action.startswith("developer."):
            from services.developer_runtime import developer_runtime

            developer_action = action.removeprefix("developer.")
            if developer_action.startswith("github."):
                return developer_runtime.execute(developer_action, payload)
            return developer_runtime.execute(action, payload)

        return {
            "status": "error",
            "message": f"Unsupported workflow action: {action}",
        }


workflow_engine = WorkflowEngine()
