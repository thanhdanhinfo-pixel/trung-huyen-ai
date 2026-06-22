from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

TaskStatus = Literal["todo", "doing", "review", "done", "blocked"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeTask:
    id: str
    title: str
    worker: str = "orchestrator"
    status: TaskStatus = "todo"
    priority: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)


class AIRuntime:
    def __init__(self) -> None:
        self.name = "TRUNG_HUYEN_AI_OS Runtime"
        self.phase = "Foundation"
        self.started_at = utc_now()
        self.tasks: List[RuntimeTask] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "name": self.name,
            "phase": self.phase,
            "started_at": self.started_at,
            "task_count": len(self.tasks),
        }

    def add_task(
        self,
        title: str,
        worker: str = "orchestrator",
        priority: int = 3,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        task = RuntimeTask(
            id=f"task-{len(self.tasks) + 1:04d}",
            title=title,
            worker=worker,
            priority=priority,
            metadata=metadata or {},
        )
        self.tasks.append(task)
        return task.__dict__

    def list_tasks(self) -> List[Dict[str, Any]]:
        return [task.__dict__ for task in self.tasks]


ai_runtime = AIRuntime()
