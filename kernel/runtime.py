from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from task_queue import Task, TaskQueue


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RuntimeTick:
    """A single Worker heartbeat/tick record."""

    index: int
    status: str = "running"
    started_at: str = field(default_factory=_now)
    ended_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def end(self, status: str, result: Dict[str, Any]) -> "RuntimeTick":
        self.status = status
        self.result = result
        self.ended_at = _now()
        return self

    def as_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "result": self.result,
        }


@dataclass
class KernelRuntime:
    """Runtime layer owned by the AI Kernel.

    This answers the Kernel question:
    "What am I doing right now?"

    During refactor this is in-memory. Later it can persist to Drive, Firestore,
    Redis or another state store without changing Worker/Planner interfaces.
    """

    current_sprint: str = "SPR-KERNEL-001"
    current_task: str = "Build AI Kernel runtime layer"
    queue: TaskQueue = field(default_factory=TaskQueue)
    tick_count: int = 0
    ticks: List[RuntimeTick] = field(default_factory=list)
    completed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    failed_tasks: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=_now)

    def enqueue(self, task: Task | Dict[str, Any]) -> Task:
        queued = self.queue.push(task)
        self.updated_at = _now()
        return queued

    def begin_tick(self) -> RuntimeTick:
        self.tick_count += 1
        tick = RuntimeTick(index=self.tick_count)
        self.ticks.append(tick)
        self.updated_at = _now()
        return tick

    def end_tick(self, tick: RuntimeTick, status: str, result: Dict[str, Any]) -> RuntimeTick:
        tick.end(status=status, result=result)
        self.updated_at = _now()
        return tick

    def record_completed(self, task: Dict[str, Any]) -> None:
        self.completed_tasks.append(task)
        self.updated_at = _now()

    def record_failed(self, task: Dict[str, Any]) -> None:
        self.failed_tasks.append(task)
        self.updated_at = _now()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "current_sprint": self.current_sprint,
            "current_task": self.current_task,
            "tick_count": self.tick_count,
            "last_tick": self.ticks[-1].as_dict() if self.ticks else None,
            "queue": self.queue.snapshot(),
            "completed_count": len(self.completed_tasks),
            "failed_count": len(self.failed_tasks),
            "updated_at": self.updated_at,
        }


runtime = KernelRuntime()
