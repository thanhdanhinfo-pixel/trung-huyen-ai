from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class QueueItem:
    id: str
    title: str
    owner: str
    capability: str
    priority: int = 3
    status: str = "queued"
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    attempts: int = 0
    max_attempts: int = 3
    error: Optional[str] = None

    def update(self, status: str, error: Optional[str] = None) -> None:
        self.status = status
        self.updated_at = utc_now()
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionQueue:
    """Hàng đợi thực thi trung tâm của Trung Huyền OS."""

    def __init__(self) -> None:
        self.items: List[QueueItem] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "execution_queue",
            "total": len(self.items),
            "queued": len([i for i in self.items if i.status == "queued"]),
            "running": len([i for i in self.items if i.status == "running"]),
            "done": len([i for i in self.items if i.status == "done"]),
            "failed": len([i for i in self.items if i.status == "failed"]),
        }

    def add(self, title: str, owner: str, capability: str, priority: int = 3, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        item = QueueItem(
            id=f"task-{len(self.items) + 1:06d}",
            title=title,
            owner=owner,
            capability=capability,
            priority=priority,
            payload=payload or {},
        )
        self.items.append(item)
        return {"status": "queued", "task": item.to_dict()}

    def bulk_add(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        created = []
        for task in tasks:
            result = self.add(
                title=task.get("title", "Untitled task"),
                owner=task.get("owner", "ai_ceo"),
                capability=task.get("capability", "core"),
                priority=int(task.get("priority", 3)),
                payload=task,
            )
            created.append(result.get("task"))
        return {"status": "queued", "count": len(created), "tasks": created}

    def next(self) -> Dict[str, Any]:
        candidates = [item for item in self.items if item.status == "queued"]
        if not candidates:
            return {"status": "empty", "task": None}
        candidates.sort(key=lambda item: (item.priority, item.created_at))
        item = candidates[0]
        item.attempts += 1
        item.update("running")
        return {"status": "running", "task": item.to_dict()}

    def complete(self, task_id: str, result: Dict[str, Any] | None = None) -> Dict[str, Any]:
        item = self._find(task_id)
        if not item:
            return {"status": "not_found", "task_id": task_id}
        item.payload["result"] = result or {}
        item.update("done")
        return {"status": "done", "task": item.to_dict()}

    def fail(self, task_id: str, error: str) -> Dict[str, Any]:
        item = self._find(task_id)
        if not item:
            return {"status": "not_found", "task_id": task_id}
        if item.attempts < item.max_attempts:
            item.update("queued", error=error)
            return {"status": "retry_queued", "task": item.to_dict()}
        item.update("failed", error=error)
        return {"status": "failed", "task": item.to_dict()}

    def list(self, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        items = self.items
        if status:
            items = [item for item in items if item.status == status]
        return {"status": "ok", "tasks": [item.to_dict() for item in items[:limit]]}

    def _find(self, task_id: str) -> Optional[QueueItem]:
        for item in self.items:
            if item.id == task_id:
                return item
        return None


execution_queue = ExecutionQueue()
