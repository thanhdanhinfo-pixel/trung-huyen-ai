from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ExecutiveRecord:
    id: str
    type: str
    title: str
    status: str = "open"
    priority: int = 5
    owner: str = "TRUNG_HUYEN_AI_OS"
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def record(self, event: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.history.append({"at": utc_now(), "event": event, "data": data or {}})
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutiveRuntime:
    """Central operating layer for TRUNG_HUYEN_AI_OS.

    ChatGPT is the advisor interface. This runtime owns execution state:
    goals, sprints, tasks, approvals, workers, memory, and reports.
    """

    def __init__(self) -> None:
        self.records: List[ExecutiveRecord] = []
        self.mode = "FOUNDATION_LOCK"

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "runtime": "executive",
            "mode": self.mode,
            "record_count": len(self.records),
            "summary": self.summary(),
        }

    def summary(self) -> Dict[str, Any]:
        by_type: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for record in self.records:
            by_type[record.type] = by_type.get(record.type, 0) + 1
            by_status[record.status] = by_status.get(record.status, 0) + 1
        return {"by_type": by_type, "by_status": by_status}

    def create(
        self,
        type: str,
        title: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        owner: str = "TRUNG_HUYEN_AI_OS",
    ) -> Dict[str, Any]:
        record = ExecutiveRecord(
            id=f"exec-{len(self.records) + 1:04d}",
            type=type,
            title=title,
            priority=priority,
            owner=owner,
            payload=payload or {},
        )
        record.record("created")
        self.records.append(record)
        return {"status": "ok", "record": record.to_dict()}

    def update(self, record_id: str, status: Optional[str] = None, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        record = self._find(record_id)
        if status:
            record.status = status
        if payload:
            record.payload.update(payload)
        record.record("updated", {"status": status, "payload": payload or {}})
        return {"status": "ok", "record": record.to_dict()}

    def approve(self, record_id: str, note: str = "") -> Dict[str, Any]:
        record = self._find(record_id)
        record.status = "approved"
        record.record("approved", {"note": note})
        return {"status": "approved", "record": record.to_dict()}

    def reject(self, record_id: str, reason: str = "") -> Dict[str, Any]:
        record = self._find(record_id)
        record.status = "rejected"
        record.record("rejected", {"reason": reason})
        return {"status": "rejected", "record": record.to_dict()}

    def list_records(self, type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        records = self.records
        if type:
            records = [record for record in records if record.type == type]
        if status:
            records = [record for record in records if record.status == status]
        return [record.to_dict() for record in sorted(records, key=lambda item: item.priority)]

    def foundation_backlog(self) -> Dict[str, Any]:
        items = [
            ("goal", "Foundation 100%", 1),
            ("sprint", "Executive Runtime", 1),
            ("sprint", "Action Registry Integration", 2),
            ("sprint", "Worker Dispatcher", 3),
            ("sprint", "Drive Runtime", 4),
            ("sprint", "Repository Manager", 5),
        ]
        created = []
        for type, title, priority in items:
            exists = any(record.type == type and record.title == title for record in self.records)
            if not exists:
                created.append(self.create(type=type, title=title, priority=priority)["record"])
        return {"status": "ok", "created": created, "summary": self.summary()}

    def _find(self, record_id: str) -> ExecutiveRecord:
        for record in self.records:
            if record.id == record_id:
                return record
        raise ValueError("Executive record not found")


executive_runtime = ExecutiveRuntime()
