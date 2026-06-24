from __future__ import annotations

from typing import Any, Dict

from services.execution_engine import execution_engine, execution_plan_from_dict


class TaskAgent:
    """Execute structured AI OS tasks.

    Supported task types:
    - execution_plan: execute a GitHub execution plan via ExecutionEngine
    - noop: return success without side effects

    This agent intentionally returns structured results instead of raising
    unhandled exceptions, so WorkflowEngine/TaskQueue can decide retry/fail.
    """

    def execute(self, task: dict) -> Dict[str, Any]:
        task_type = task.get("type", "noop")

        try:
            if task_type == "execution_plan":
                return self._execute_plan(task)
            if task_type == "noop":
                return self._noop(task)

            return {
                "status": "error",
                "task_type": task_type,
                "error_type": "UnsupportedTaskType",
                "message": f"Unsupported task type: {task_type}",
                "task": task,
            }

        except Exception as exc:
            return {
                "status": "error",
                "task_type": task_type,
                "error_type": type(exc).__name__,
                "message": str(exc),
                "task": task,
            }

    def _execute_plan(self, task: dict) -> Dict[str, Any]:
        payload = task.get("payload") or {}
        plan_data = payload.get("plan") or {}
        approved = bool(payload.get("approved", False))

        if not isinstance(plan_data, dict):
            return {
                "status": "error",
                "task_type": "execution_plan",
                "error_type": "ValidationError",
                "message": "payload.plan must be an object",
                "task": task,
            }

        plan = execution_plan_from_dict(plan_data)
        result = execution_engine.execute(plan=plan, approved=approved)

        return {
            "status": result.get("status", "error"),
            "task_type": "execution_plan",
            "result": result,
            "task": task,
        }

    def _noop(self, task: dict) -> Dict[str, Any]:
        return {
            "status": "ok",
            "task_type": "noop",
            "message": "No operation executed.",
            "task": task,
        }
