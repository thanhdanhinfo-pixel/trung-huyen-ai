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
    """Validate audit record structure without acting as an authorization gate.

    RULE-020: SINGLE GRANT AUTHORITY
    - Founder Grant is the source of truth for write authorization.
    - Audit is a logging / traceability layer.
    - Audit must not block a write that has already passed Founder Grant validation.
    """
    if not isinstance(record, dict):
        return False

    return bool(record.get("event") and record.get("timestamp"))
