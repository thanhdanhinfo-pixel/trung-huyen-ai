from datetime import datetime, timezone
import json


def write_audit(event: str, data: dict) -> dict:
    record = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **data,
    }

    print("[AUDIT]", json.dumps(record, ensure_ascii=False))

    return record


def require_audit(record: dict) -> bool:
    required = [
        "event",
        "timestamp",
        "approved_by",
        "approval_id",
    ]

    return all(record.get(k) for k in required)
