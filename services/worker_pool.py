from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.execution_queue import execution_queue


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Worker:
    id: str
    capability: str
    status: str = "idle"
    current_task_id: Optional[str] = None
    completed: int = 0
    failed: int = 0
    last_seen_at: str = field(default_factory=utc_now)

    def touch(self) -> None:
        self.last_seen_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkerPool:
    """Nhóm xử lý tác vụ của Trung Huyền OS.

    Phiên bản nền tảng: quản lý worker, nhận task từ ExecutionQueue,
    hoàn thành/thất bại task và ghi trạng thái worker.
    """

    def __init__(self) -> None:
        self.workers: List[Worker] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "worker_pool",
            "worker_count": len(self.workers),
            "idle": len([w for w in self.workers if w.status == "idle"]),
            "busy": len([w for w in self.workers if w.status == "busy"]),
            "error": len([w for w in self.workers if w.status == "error"]),
            "workers": [w.to_dict() for w in self.workers],
        }

    def register(self, capability: str, worker_id: Optional[str] = None) -> Dict[str, Any]:
        worker = Worker(
            id=worker_id or f"worker-{len(self.workers) + 1:04d}",
            capability=capability,
        )
        self.workers.append(worker)
        return {"status": "registered", "worker": worker.to_dict()}

    def assign_next(self, capability: Optional[str] = None) -> Dict[str, Any]:
        worker = self._find_idle_worker(capability)
        if not worker:
            return {"status": "no_idle_worker"}
        task_result = execution_queue.next()
        task = task_result.get("task")
        if not task:
            return {"status": "no_task"}
        if capability and task.get("capability") != capability:
            execution_queue.fail(task.get("id"), f"Capability mismatch: {task.get('capability')} != {capability}")
            return {"status": "capability_mismatch", "task": task}
        worker.status = "busy"
        worker.current_task_id = task.get("id")
        worker.touch()
        return {"status": "assigned", "worker": worker.to_dict(), "task": task}

    def complete(self, worker_id: str, result: Dict[str, Any] | None = None) -> Dict[str, Any]:
        worker = self._find(worker_id)
        if not worker:
            return {"status": "worker_not_found", "worker_id": worker_id}
        if not worker.current_task_id:
            return {"status": "no_current_task", "worker": worker.to_dict()}
        task_id = worker.current_task_id
        queue_result = execution_queue.complete(task_id, result=result or {})
        worker.completed += 1
        worker.status = "idle"
        worker.current_task_id = None
        worker.touch()
        return {"status": "done", "worker": worker.to_dict(), "queue": queue_result}

    def fail(self, worker_id: str, error: str) -> Dict[str, Any]:
        worker = self._find(worker_id)
        if not worker:
            return {"status": "worker_not_found", "worker_id": worker_id}
        if not worker.current_task_id:
            worker.status = "error"
            worker.failed += 1
            worker.touch()
            return {"status": "worker_error", "worker": worker.to_dict()}
        task_id = worker.current_task_id
        queue_result = execution_queue.fail(task_id, error=error)
        worker.failed += 1
        worker.status = "idle"
        worker.current_task_id = None
        worker.touch()
        return {"status": "failed", "worker": worker.to_dict(), "queue": queue_result}

    def _find_idle_worker(self, capability: Optional[str] = None) -> Optional[Worker]:
        for worker in self.workers:
            if worker.status != "idle":
                continue
            if capability and worker.capability != capability:
                continue
            return worker
        return None

    def _find(self, worker_id: str) -> Optional[Worker]:
        for worker in self.workers:
            if worker.id == worker_id:
                return worker
        return None


worker_pool = WorkerPool()
