from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkerRegistry:
    """Danh bạ AI Worker của Trung Huyền OS."""

    def __init__(self) -> None:
        self.workers: Dict[str, Dict[str, Any]] = {}

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "worker_registry",
            "worker_count": len(self.workers),
            "workers": list(self.workers.values()),
        }

    def register(
        self,
        worker_id: str,
        role: str,
        capability: str,
        owner: str = "ai_ceo",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        worker = {
            "worker_id": worker_id,
            "role": role,
            "capability": capability,
            "owner": owner,
            "status": "idle",
            "current_task_id": None,
            "registered_at": now(),
            "last_heartbeat_at": now(),
            "completed": 0,
            "failed": 0,
            "metadata": metadata or {},
        }
        self.workers[worker_id] = worker
        return {"status": "registered", "worker": worker}

    def heartbeat(self, worker_id: str) -> Dict[str, Any]:
        worker = self.workers.get(worker_id)
        if not worker:
            return {"status": "not_found", "worker_id": worker_id}
        worker["last_heartbeat_at"] = now()
        return {"status": "ok", "worker": worker}

    def set_status(self, worker_id: str, status: str, task_id: str | None = None) -> Dict[str, Any]:
        worker = self.workers.get(worker_id)
        if not worker:
            return {"status": "not_found", "worker_id": worker_id}
        worker["status"] = status
        worker["current_task_id"] = task_id
        worker["last_heartbeat_at"] = now()
        return {"status": "ok", "worker": worker}

    def find_idle(self, capability: str | None = None) -> Dict[str, Any]:
        for worker in self.workers.values():
            if worker.get("status") != "idle":
                continue
            if capability and worker.get("capability") != capability:
                continue
            return {"status": "found", "worker": worker}
        return {"status": "not_found", "worker": None}

    def complete(self, worker_id: str) -> Dict[str, Any]:
        worker = self.workers.get(worker_id)
        if not worker:
            return {"status": "not_found", "worker_id": worker_id}
        worker["completed"] += 1
        worker["status"] = "idle"
        worker["current_task_id"] = None
        worker["last_heartbeat_at"] = now()
        return {"status": "ok", "worker": worker}

    def fail(self, worker_id: str) -> Dict[str, Any]:
        worker = self.workers.get(worker_id)
        if not worker:
            return {"status": "not_found", "worker_id": worker_id}
        worker["failed"] += 1
        worker["status"] = "idle"
        worker["current_task_id"] = None
        worker["last_heartbeat_at"] = now()
        return {"status": "ok", "worker": worker}

    def bootstrap_defaults(self) -> Dict[str, Any]:
        defaults = [
            ("worker-dev", "Dev Worker", "development"),
            ("worker-runtime", "Runtime Worker", "runtime"),
            ("worker-security", "Security Worker", "security"),
            ("worker-knowledge", "Knowledge Worker", "knowledge"),
            ("worker-qa", "QA Worker", "quality"),
            ("worker-monitoring", "Monitoring Worker", "monitoring"),
        ]
        created = []
        for worker_id, role, capability in defaults:
            if worker_id not in self.workers:
                created.append(self.register(worker_id, role, capability))
        return {"status": "bootstrapped", "created": created, "registry": self.status()}


worker_registry = WorkerRegistry()
