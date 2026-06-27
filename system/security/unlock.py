from datetime import datetime, timezone


UNLOCK_MODE = "FOUNDER_UNLOCK_MODE"


def create_founder_unlock(
    level: int,
    reason: str,
    session_id: str = "",
) -> dict:
    return {
        "mode": UNLOCK_MODE,
        "level": level,
        "approved_by": "Founder",
        "reason": reason,
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }


def is_founder_unlock_active(data: dict, min_level: int = 1) -> bool:
    if not isinstance(data, dict):
        return False

    if data.get("mode") != UNLOCK_MODE:
        return False

    if data.get("approved_by") != "Founder":
        return False

    if data.get("status") != "active":
        return False

    try:
        return int(data.get("level", 0)) >= min_level
    except Exception:
        return False
