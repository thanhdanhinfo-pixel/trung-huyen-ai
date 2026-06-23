from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.execution_queue import execution_queue
from services.worker_pool import worker_pool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SupervisorReport:
    status: str
    created_at: str = field(default_factory=utc_now)
    queue: Dict[str, Any] = field(default_factory=dict)
    workers: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class Supervisor:
    """Bộ giám sát điều phối worker và hàng đợi."""

    def __init__(self) -> None:
        self.reports: List[Dict[str, Any]] = []

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "supervisor",
            "report_count": len(self.reports),
            "latest": self.reports[-1] if self.reports else None,
        }

    def inspect(self) -> Dict[str, Any]:
        report = SupervisorReport(
            status="ok",
            queue=execution_queue.status(),
            workers=worker_pool.status(),
        )
        self.reports.append(report.to_dict())
        return report.to_dict()

    def balance(self, capability: str | None = None) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []
        while True:
            assigned = worker_pool.assign_next(capability=capability)
            if assigned.get("status") not in {"assigned"}:
                actions.append(assigned)
                break
            actions.append(assigned)
        report = SupervisorReport(
            status="balanced",
            queue=execution_queue.status(),
            workers=worker_pool.status(),
            actions=actions,
        )
        self.reports.append(report.to_dict())
        return report.to_dict()


supervisor = Supervisor()
