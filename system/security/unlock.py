from datetime import datetime, timezone

UNLOCK_MODE = "FOUNDER_UNLOCK_MODE"
REGISTERED_LOCKS = []
_SYSTEM_UNLOCK_STATE = {
    "active": False,
    "reason": "",
}


def register_lock(handler):
    REGISTERED_LOCKS.append(handler)
    return handler


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


def open_all_locks(reason: str = "Founder command") -> dict:
    _SYSTEM_UNLOCK_STATE["active"] = True
    _SYSTEM_UNLOCK_STATE["reason"] = reason

    unlock = create_founder_unlock(
        level=5,
        reason=reason,
        session_id="UNIFIED-UNLOCK",
    )

    results = []
    for handler in REGISTERED_LOCKS:
        try:
            results.append(handler())
        except Exception as exc:
            results.append({"status": "error", "error": str(exc)})

    return {
        "status": "ok",
        "unlock": unlock,
        "locks_opened": len(results),
        "results": results,
    }


def is_system_unlocked() -> bool:
    return _SYSTEM_UNLOCK_STATE["active"]
