from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    goal: str
    type: str = "generic"
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: _now())
    updated_at: str = field(default_factory=lambda: _now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "type": self.type,
            "payload": self.payload,
            "priority": self.priority,
            "status": self.status.value,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskQueue:
    """In-memory task queue with structured lifecycle.

    This is the first production-ready layer over the old list-based queue.
    A later version can persist tasks to Drive, Firestore, Redis or a database
    without changing the public interface.
    """

    def __init__(self):
        self.tasks: List[Task] = []
        self.history: List[Task] = []

    def push(self, task: Task | Dict[str, Any]) -> Task:
        if isinstance(task, dict):
            task = Task(
                goal=task.get("goal", ""),
                type=task.get("type", "generic"),
                payload=task.get("payload", {}),
                priority=int(task.get("priority", 100)),
                max_attempts=int(task.get("max_attempts", 3)),
            )

        if not task.goal:
            raise ValueError("task.goal is required")

        task.status = TaskStatus.PENDING
        task.updated_at = _now()
        self.tasks.append(task)
        self.tasks.sort(key=lambda item: (item.priority, item.created_at))
        return task

    def pop(self) -> Optional[Task]:
        if not self.tasks:
            return None

        task = self.tasks.pop(0)
        task.status = TaskStatus.RUNNING
        task.attempts += 1
        task.updated_at = _now()
        return task

    def complete(self, task: Task, result: Optional[Dict[str, Any]] = None) -> Task:
        task.status = TaskStatus.COMPLETED
        task.result = result or {}
        task.updated_at = _now()
        self.history.append(task)
        return task

    def fail(self, task: Task, error: Dict[str, Any]) -> Task:
        task.error = error
        task.updated_at = _now()

        if task.attempts < task.max_attempts:
            task.status = TaskStatus.PENDING
            self.tasks.append(task)
            self.tasks.sort(key=lambda item: (item.priority, item.created_at))
        else:
            task.status = TaskStatus.FAILED
            self.history.append(task)

        return task

    def cancel(self, task_id: str) -> Optional[Task]:
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                removed = self.tasks.pop(index)
                removed.status = TaskStatus.CANCELLED
                removed.updated_at = _now()
                self.history.append(removed)
                return removed
        return None

    def list_pending(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.tasks]

    def list_history(self) -> List[Dict[str, Any]]:
        return [task.to_dict() for task in self.history]

    def snapshot(self) -> Dict[str, Any]:
        return {
            "pending": self.list_pending(),
            "history": self.list_history(),
            "pending_count": len(self.tasks),
            "history_count": len(self.history),
        }
