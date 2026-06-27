from datetime import datetime, timezone
from uuid import UUID


def validate_founder_approval(data: dict) -> bool:

    if data.get("approved_by") != "Founder":
        return False

    try:
        UUID(data["approval_id"])
    except Exception:
        return False

    try:
        datetime.fromisoformat(
            data["approved_at"].replace("Z", "+00:00")
        )
    except Exception:
        return False

    reason = data.get("reason", "").strip()

    if not reason:
        return False

    return True
