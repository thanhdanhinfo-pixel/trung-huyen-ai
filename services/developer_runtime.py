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
    rollback-safe operations, and batch execution.
    """

    def __init__(self) -> None:
        self.tasks: List[DeveloperTask] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "developer",
            "task_count": len(self.tasks),
            "github": github_runtime.status(),
            "actions": [
                "github.status",
                "github.read",
                "github.patch",
                "github.verify",
                "github.rollback",
                "workflow.batch",
            ],
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

        if action == "workflow.batch":
            return self.batch_execute(payload=payload, task=task)

        return {"status": "error", "message": f"Unsupported action: {action}"}

    def batch_execute(self, payload: Dict[str, Any], task: DeveloperTask) -> Dict[str, Any]:
        steps = payload.get("steps", [])
        rollback_on_error = bool(payload.get("rollback_on_error", True))
        stop_on_error = bool(payload.get("stop_on_error", True))

        if not isinstance(steps, list) or not steps:
            return {"status": "blocked", "message": "workflow.batch requires a non-empty steps list."}

        report: Dict[str, Any] = {
            "status": "running",
            "step_count": len(steps),
            "completed": 0,
            "failed": 0,
            "steps": [],
            "rollback_results": [],
        }
        rollback_stack: List[Dict[str, Any]] = []
        task.record("batch_started", {"step_count": len(steps)})

        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                step_result = {"status": "failed", "message": "Step must be an object", "index": index}
            else:
                action = step.get("action", "")
                step_payload = step.get("payload", {}) or {}
                task.record("batch_step_started", {"index": index, "action": action})
                step_result = self._execute_action(action, step_payload, task)
                step_result = {
                    "index": index,
                    "action": action,
                    "status": step_result.get("status", "unknown"),
                    "result": step_result,
                }

                rollback_info = step_result.get("result", {}).get("rollback")
                if isinstance(rollback_info, dict) and rollback_info.get("available"):
                    rollback_stack.append(rollback_info)

            report["steps"].append(step_result)
            if step_result.get("status") in {"error", "failed", "blocked"}:
                report["failed"] += 1
                task.record("batch_step_failed", step_result)
                if rollback_on_error:
                    report["rollback_results"] = self.rollback_batch(rollback_stack, task)
                if stop_on_error:
                    report["status"] = "failed"
                    task.record("batch_stopped", {"failed_at": index})
                    return report
            else:
                report["completed"] += 1
                task.record("batch_step_done", {"index": index, "status": step_result.get("status")})

        report["status"] = "done" if report["failed"] == 0 else "failed"
        task.record("batch_finished", report)
        return report

    def rollback_batch(self, rollback_stack: List[Dict[str, Any]], task: DeveloperTask) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for item in reversed(rollback_stack):
            previous_content = item.get("previous_content")
            path = item.get("path")
            if not path or previous_content is None:
                results.append({"status": "skipped", "message": "Missing rollback path or previous_content"})
                continue
            result = self.rollback_file(
                payload={
                    "path": path,
                    "previous_content": previous_content,
                    "message": f"Rollback batch change for {path}",
                },
                task=task,
            )
            results.append(result)
        return results

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
