from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from services.developer_runtime import developer_runtime
from services.runtime_diagnostic import runtime_diagnostic
from services.security_center import security_center


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AIWorker:
    """AI Worker thực thi task theo capability.

    Phiên bản V1 tập trung vào điều phối công cụ nội bộ đã có:
    development, diagnostic, security, monitoring, knowledge.
    """

    def execute(self, worker: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        capability = task.get("capability") or worker.get("capability") or "general"
        payload = task.get("payload") or {}
        action = payload.get("action") or task.get("title", "")

        security = security_center.assess_risk(action=capability, payload=payload)
        if security.get("risk") == "high" and not payload.get("approved"):
            return {
                "status": "blocked",
                "reason": "high_risk_requires_approval",
                "worker_id": worker.get("worker_id"),
                "task_id": task.get("id"),
                "security": security,
                "completed_at": now(),
            }

        if capability == "development":
            return self._execute_development(worker, task, payload)
        if capability == "diagnostic":
            return self._execute_diagnostic(worker, task)
        if capability == "security":
            return self._execute_security(worker, task, payload)
        if capability == "monitoring":
            return self._execute_monitoring(worker, task)
        if capability == "knowledge":
            return self._execute_knowledge(worker, task)

        return {
            "status": "done",
            "mode": "acknowledged",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": capability,
            "message": "Task acknowledged. No specialized executor yet.",
            "completed_at": now(),
        }

    def _execute_development(self, worker: Dict[str, Any], task: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        files = payload.get("files") or []
        operations = payload.get("operations") or []
        if files:
            result = developer_runtime.patch(
                files=files,
                message=payload.get("message", "AI Worker development patch"),
                commit=bool(payload.get("commit", False)),
            )
        elif operations:
            result = developer_runtime.batch(
                operations=operations,
                message=payload.get("message", "AI Worker development batch"),
                commit=bool(payload.get("commit", False)),
            )
        else:
            result = developer_runtime.status()
        return {
            "status": "done",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": "development",
            "result": result,
            "completed_at": now(),
        }

    def _execute_diagnostic(self, worker: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        result = runtime_diagnostic.github_status()
        return {
            "status": "done",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": "diagnostic",
            "result": result,
            "completed_at": now(),
        }

    def _execute_security(self, worker: Dict[str, Any], task: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        result = security_center.assess_risk(
            action=payload.get("action", "security.review"),
            payload=payload,
        )
        return {
            "status": "done",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": "security",
            "result": result,
            "completed_at": now(),
        }

    def _execute_monitoring(self, worker: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        result = runtime_diagnostic.version()
        return {
            "status": "done",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": "monitoring",
            "result": result,
            "completed_at": now(),
        }

    def _execute_knowledge(self, worker: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "done",
            "worker_id": worker.get("worker_id"),
            "task_id": task.get("id"),
            "capability": "knowledge",
            "message": "Knowledge worker acknowledged. Learning engine will handle this in V2.",
            "completed_at": now(),
        }


ai_worker = AIWorker()
