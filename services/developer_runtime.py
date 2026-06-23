from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.github_runtime import github_runtime


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DeveloperTask:
    id: str
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "created"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    result: Dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeveloperRuntime:
    """Developer execution layer.

    API routers and future Workflow Runner should call this class instead of
    calling GitHubRuntime directly. GitHubRuntime remains the infrastructure
    adapter; this class owns developer actions, task log, and execution policy.
    """

    def __init__(self) -> None:
        self.tasks: List[DeveloperTask] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "developer",
            "task_count": len(self.tasks),
            "github": github_runtime.status(),
        }

    def _record(self, action: str, payload: Dict[str, Any]) -> DeveloperTask:
        task = DeveloperTask(
            id=f"dev-task-{len(self.tasks) + 1:04d}",
            action=action,
            payload=payload,
        )
        self.tasks.append(task)
        return task

    def execute(self, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        task = self._record(action=action, payload=payload)
        task.status = "running"
        task.updated_at = utc_now()

        try:
            if action == "github.status":
                result = github_runtime.status()
            elif action == "github.read":
                result = github_runtime.read_file(payload.get("path", ""))
            elif action == "github.patch":
                result = github_runtime.patch_file(
                    path=payload.get("path", ""),
                    operations=payload.get("operations", []),
                    message=payload.get("message", "Developer Runtime patch"),
                    commit=bool(payload.get("commit", False)),
                )
            else:
                result = {
                    "status": "error",
                    "message": f"Unsupported action: {action}",
                }

            task.result = result
            task.status = "done" if result.get("status") != "error" else "failed"
            task.updated_at = utc_now()
            return {
                "status": task.status,
                "task": task.to_dict(),
                "result": result,
            }
        except Exception as exc:
            task.status = "failed"
            task.error = f"{type(exc).__name__}: {exc}"
            task.updated_at = utc_now()
            return {
                "status": "failed",
                "task": task.to_dict(),
                "error": task.error,
            }

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.tasks]


developer_runtime = DeveloperRuntime()
