from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.workflow_engine import workflow_engine


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class WorkerRun:
    id: str
    status: str = "created"
    requested_at: str = field(default_factory=utc_now)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    max_tasks: int = 10
    processed: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkerRuntime:
    """Internal worker runner for the current Cloud Run service.

    This is the safe first stage before splitting a separate Cloud Run worker.
    It drains WorkflowEngine queued tasks when called by an endpoint, scheduler,
    or future background runner.
    """

    def __init__(self) -> None:
        self.runs: List[WorkerRun] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "worker",
            "run_count": len(self.runs),
            "workflow": workflow_engine.status(),
        }

    def run_once(self, max_tasks: int = 10) -> Dict[str, Any]:
        run = WorkerRun(id=f"worker-run-{len(self.runs) + 1:04d}", max_tasks=max_tasks)
        self.runs.append(run)
        run.status = "running"
        run.started_at = utc_now()

        try:
            for task in workflow_engine.next_runnable(limit=max_tasks):
                result = workflow_engine.run(task["id"])
                run.results.append(result)
                run.processed += 1

            run.status = "done"
            run.finished_at = utc_now()
            return {"status": "done", "run": run.to_dict()}
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.error = f"{type(exc).__name__}: {exc}"
            run.finished_at = utc_now()
            return {"status": "failed", "run": run.to_dict(), "error": run.error}

    def history(self) -> List[Dict[str, Any]]:
        return [run.to_dict() for run in self.runs]


worker_runtime = WorkerRuntime()
