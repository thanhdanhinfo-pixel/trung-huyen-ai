from datetime import datetime
from uuid import UUID


def validate_founder_approval(data: dict) -> bool:

    # Founder Grant V2 (ưu tiên cao nhất)
    grant_token = data.get("grant_token")

    if grant_token:
        try:
            UUID(str(grant_token))
            return True
        except Exception:
            pass

    # Legacy approval flow
    if data.get("approved_by") != "Founder":
        return False

    try:
        UUID(str(data["approval_id"]))
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
