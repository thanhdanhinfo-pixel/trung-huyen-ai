from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.workflow_engine import workflow_engine


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DeveloperWorkerRun:
    id: str
    workflow: Dict[str, Any]
    status: str = "created"
    created_at: str = field(default_factory=utc_now)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeveloperWorker:
    """Developer worker for executing developer workflows.

    This is the worker-facing layer above WorkflowEngine. It accepts a workflow
    payload, submits it to the WorkflowEngine, and keeps worker execution logs.
    """

    def __init__(self) -> None:
        self.runs: List[DeveloperWorkerRun] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "worker": "developer",
            "run_count": len(self.runs),
            "workflow": workflow_engine.status(),
        }

    def execute(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        run = DeveloperWorkerRun(
            id=f"developer-worker-run-{len(self.runs) + 1:04d}",
            workflow=workflow,
        )
        self.runs.append(run)
        run.status = "running"
        run.started_at = utc_now()

        try:
            action = workflow.get("action", "workflow.batch")
            payload = workflow.get("payload", workflow)
            requires_approval = bool(workflow.get("requires_approval", False))
            auto_run = bool(workflow.get("auto_run", True))

            result = workflow_engine.submit(
                action=f"developer.{action}" if not action.startswith("developer.") else action,
                payload=payload,
                requires_approval=requires_approval,
                auto_run=auto_run,
            )

            run.result = result
            run.status = "done" if result.get("status") not in {"failed", "error"} else "failed"
            run.finished_at = utc_now()
            return {"status": run.status, "run": run.to_dict(), "result": result}
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.error = f"{type(exc).__name__}: {exc}"
            run.finished_at = utc_now()
            return {"status": "failed", "run": run.to_dict(), "error": run.error}

    def history(self) -> List[Dict[str, Any]]:
        return [run.to_dict() for run in self.runs]


developer_worker = DeveloperWorker()
