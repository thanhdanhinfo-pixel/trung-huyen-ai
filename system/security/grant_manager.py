from datetime import datetime, timezone

LEVEL_READ_ONLY = 0
LEVEL_SAFE_WRITE = 1
LEVEL_SYSTEM_REFACTOR = 2
LEVEL_FULL_SYSTEM_ACCESS = 3

STATUS_ACTIVE = "active"
STATUS_REVOKED = "revoked"
STATUS_COMPLETED = "completed"

SCOPE_ALL_SYSTEM = "ALL_SYSTEM"


def create_founder_grant(
    granted_to: str,
    level: int,
    scope: str,
    reason: str,
    session_id: str = "",
) -> dict:
    return {
        "mode": "FOUNDER_GRANT_MODE",
        "granted_by": "Founder",
        "granted_to": granted_to,
        "level": level,
        "scope": scope,
        "reason": reason,
        "session_id": session_id,
        "status": STATUS_ACTIVE,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def is_founder_grant_active(
    data: dict,
    subject: str,
    min_level: int = LEVEL_SAFE_WRITE,
    scope: str = SCOPE_ALL_SYSTEM,
) -> bool:
    if not isinstance(data, dict):
        return False

    if data.get("mode") != "FOUNDER_GRANT_MODE":
        return False

    if data.get("granted_by") != "Founder":
        return False

    if data.get("granted_to") != subject:
        return False

    if data.get("status") != STATUS_ACTIVE:
        return False

    if data.get("scope") not in {scope, SCOPE_ALL_SYSTEM}:
        return False

    try:
        return int(data.get("level", 0)) >= min_level
    except Exception:
        return False


def revoke_founder_grant(data: dict, reason: str = "manual revoke") -> dict:
    updated = dict(data or {})
    updated["status"] = STATUS_REVOKED
    updated["revoked_at"] = datetime.now(timezone.utc).isoformat()
    updated["revoke_reason"] = reason
    return updated


def complete_founder_grant(data: dict, reason: str = "task completed") -> dict:
    updated = dict(data or {})
    updated["status"] = STATUS_COMPLETED
    updated["completed_at"] = datetime.now(timezone.utc).isoformat()
    updated["complete_reason"] = reason
    return updated
