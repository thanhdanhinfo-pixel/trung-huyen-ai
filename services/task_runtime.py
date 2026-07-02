from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Dict, Optional


@dataclass
class RuntimeTask:
    id: str
    title: str
    status: str = "RUNNING"
    started_at: str = ""
    eta_seconds: int = 300
    progress: int = 0
    current_step: str = "Đang chuẩn bị"
    cloud_run_delay_seconds: int = 0
    build_id: Optional[str] = None
    completed_at: Optional[str] = None


class TaskRuntimeManager:
    def __init__(self) -> None:
        self._lock = RLock()
        self._tasks: Dict[str, RuntimeTask] = {}

    def start(
        self,
        task_id: str,
        title: str,
        eta_seconds: int = 300,
        current_step: str = "Đang chuẩn bị",
        build_id: Optional[str] = None,
        cloud_run_delay_seconds: int = 0,
    ) -> Dict:
        with self._lock:
            task = RuntimeTask(
                id=task_id,
                title=title,
                status="RUNNING",
                started_at=datetime.now(timezone.utc).isoformat(),
                eta_seconds=max(1, int(eta_seconds)),
                progress=1,
                current_step=current_step,
                build_id=build_id,
                cloud_run_delay_seconds=max(0, int(cloud_run_delay_seconds)),
            )
            self._tasks[task_id] = task
            return self._enrich(task)

    def update(self, task_id: str, **updates) -> Dict:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return {"status": "not_found", "id": task_id}
            for key, value in updates.items():
                if hasattr(task, key) and value is not None:
                    setattr(task, key, value)
            return self._enrich(task)

    def complete(self, task_id: str, status: str = "DONE") -> Dict:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return {"status": "not_found", "id": task_id}
            task.status = status
            task.progress = 100
            task.current_step = "Hoàn thành"
            task.cloud_run_delay_seconds = 0
            task.completed_at = datetime.now(timezone.utc).isoformat()
            return self._enrich(task)

    def active(self) -> Dict[str, Dict]:
        with self._lock:
            return {
                task_id: self._enrich(task)
                for task_id, task in self._tasks.items()
            }

    def _enrich(self, task: RuntimeTask) -> Dict:
        data = asdict(task)
        try:
            started = datetime.fromisoformat(task.started_at.replace("Z", "+00:00"))
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            data["remaining_seconds"] = max(0, int(task.eta_seconds - elapsed))
        except Exception:
            data["remaining_seconds"] = task.eta_seconds
        return data


task_runtime = TaskRuntimeManager()
