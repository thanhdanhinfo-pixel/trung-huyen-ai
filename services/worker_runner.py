from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from services.ai_worker import ai_worker
from services.execution_queue import execution_queue
from services.worker_registry import worker_registry


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkerRunner:
    """Bộ điều phối chạy AI Worker.

    Nhận task từ ExecutionQueue, chọn worker phù hợp trong WorkerRegistry,
    giao việc cho AIWorker, cập nhật kết quả và trạng thái.
    """

    def __init__(self) -> None:
        self.run_count = 0
        self.last_result: Dict[str, Any] | None = None

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "worker_runner",
            "run_count": self.run_count,
            "last_result": self.last_result,
            "registry": worker_registry.status(),
            "queue": execution_queue.status(),
        }

    def bootstrap(self) -> Dict[str, Any]:
        registry = worker_registry.bootstrap_defaults()
        return {
            "status": "bootstrapped",
            "registry": registry,
            "runner": self.status(),
        }

    def enqueue_task(
        self,
        title: str,
        capability: str,
        owner: str = "ai_ceo",
        priority: int = 3,
        payload: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return execution_queue.add(
            title=title,
            owner=owner,
            capability=capability,
            priority=priority,
            payload=payload or {},
        )

    def run_once(self, capability: str | None = None) -> Dict[str, Any]:
        self.run_count += 1

        next_task = execution_queue.next()
        task = next_task.get("task")
        if not task:
            result = {
                "status": "idle",
                "message": "No queued task",
                "ran_at": now(),
                "queue": execution_queue.status(),
            }
            self.last_result = result
            return result

        task_capability = capability or task.get("capability")
        worker_result = worker_registry.find_idle(capability=task_capability)
        worker = worker_result.get("worker")
        if not worker:
            execution_queue.fail(task.get("id"), f"No idle worker for capability: {task_capability}")
            result = {
                "status": "no_worker",
                "task": task,
                "capability": task_capability,
                "ran_at": now(),
            }
            self.last_result = result
            return result

        worker_registry.set_status(worker_id=worker.get("worker_id"), status="busy", task_id=task.get("id"))
        execution_result = ai_worker.execute(worker=worker, task=task)

        if execution_result.get("status") in {"done", "ok"}:
            queue_result = execution_queue.complete(task.get("id"), result=execution_result)
            registry_result = worker_registry.complete(worker.get("worker_id"))
            final_status = "done"
        else:
            queue_result = execution_queue.fail(task.get("id"), error=str(execution_result))
            registry_result = worker_registry.fail(worker.get("worker_id"))
            final_status = "failed"

        result = {
            "status": final_status,
            "worker": worker,
            "task": task,
            "execution": execution_result,
            "queue": queue_result,
            "registry": registry_result,
            "ran_at": now(),
        }
        self.last_result = result
        return result

    def run_batch(self, limit: int = 5, capability: str | None = None) -> Dict[str, Any]:
        results = []
        for _ in range(max(1, min(limit, 50))):
            result = self.run_once(capability=capability)
            results.append(result)
            if result.get("status") in {"idle", "no_worker"}:
                break
        return {
            "status": "ok",
            "count": len(results),
            "results": results,
            "queue": execution_queue.status(),
            "registry": worker_registry.status(),
        }


worker_runner = WorkerRunner()
