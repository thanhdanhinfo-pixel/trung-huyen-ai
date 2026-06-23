from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)

    def record(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.history.append({"at": utc_now(), "event": event, "data": data or {}})
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeveloperRuntime:
    """Developer execution layer.

    WorkflowEngine submits developer actions here. GitHubRuntime remains the
    infrastructure adapter. This class owns execution policy, task log, verify,
    and rollback-safe operations.
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
        task.record("created", {"action": action})
        self.tasks.append(task)
        return task

    def execute(self, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = payload or {}
        task = self._record(action=action, payload=payload)
        task.status = "running"
        task.record("running")

        try:
            result = self._execute_action(action, payload, task)
            task.result = result
            task.status = "done" if result.get("status") not in {"error", "failed", "blocked"} else "failed"
            task.record(task.status, {"result": result})
            return {"status": task.status, "task": task.to_dict(), "result": result}
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error = f"{type(exc).__name__}: {exc}"
            task.record("failed", {"error": task.error})
            return {"status": "failed", "task": task.to_dict(), "error": task.error}

    def _execute_action(self, action: str, payload: Dict[str, Any], task: DeveloperTask) -> Dict[str, Any]:
        if action == "github.status":
            return github_runtime.status()

        if action == "github.read":
            return github_runtime.read_file(payload.get("path", ""))

        if action == "github.verify":
            return self.verify_file(
                path=payload.get("path", ""),
                expected_content=payload.get("expected_content"),
            )

        if action == "github.patch":
            return self.patch_file(payload=payload, task=task)

        if action == "github.rollback":
            return self.rollback_file(payload=payload, task=task)

        return {"status": "error", "message": f"Unsupported action: {action}"}

    def patch_file(self, payload: Dict[str, Any], task: DeveloperTask) -> Dict[str, Any]:
        path = payload.get("path", "")
        before = github_runtime.read_file(path)
        before_content = before.get("content", "")
        task.record("snapshot_before_patch", {"path": path, "sha": before.get("sha")})

        result = github_runtime.patch_file(
            path=path,
            operations=payload.get("operations", []),
            message=payload.get("message", "Developer Runtime patch"),
            commit=bool(payload.get("commit", False)),
        )

        result.setdefault("rollback", {})
        result["rollback"].update({
            "available": True,
            "path": path,
            "previous_sha": before.get("sha"),
            "previous_content": before_content,
        })

        if bool(payload.get("commit", False)) and result.get("status") == "committed":
            verify = github_runtime.read_file(path)
            result["post_commit_verify"] = {
                "verified": verify.get("content") != before_content,
                "path": path,
                "sha": verify.get("sha"),
            }
            task.record("post_commit_verify", result["post_commit_verify"])

        return result

    def verify_file(self, path: str, expected_content: Optional[str] = None) -> Dict[str, Any]:
        current = github_runtime.read_file(path)
        if expected_content is None:
            return {
                "status": "ok",
                "path": path,
                "sha": current.get("sha"),
                "content_length": len(current.get("content", "")),
            }
        return {
            "status": "ok" if current.get("content") == expected_content else "failed",
            "path": path,
            "sha": current.get("sha"),
            "verified": current.get("content") == expected_content,
        }

    def rollback_file(self, payload: Dict[str, Any], task: DeveloperTask) -> Dict[str, Any]:
        path = payload.get("path", "")
        previous_content = payload.get("previous_content")
        if not path or previous_content is None:
            return {
                "status": "blocked",
                "message": "Rollback requires path and previous_content.",
            }

        current = github_runtime.read_file(path)
        result = github_runtime.update_file(
            path=path,
            content=previous_content,
            message=payload.get("message", "Rollback file to previous content"),
            sha=current.get("sha"),
        )
        verify = self.verify_file(path=path, expected_content=previous_content)
        task.record("rollback_verify", verify)
        return {
            "status": "rolled_back" if verify.get("verified") else "failed",
            "path": path,
            "commit": result.get("commit", {}),
            "verify": verify,
        }

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.tasks]

    def get_task(self, task_id: str) -> Dict[str, Any]:
        for task in self.tasks:
            if task.id == task_id:
                return task.to_dict()
        raise ValueError("Developer task not found")


developer_runtime = DeveloperRuntime()
