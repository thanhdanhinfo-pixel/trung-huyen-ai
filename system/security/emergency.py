from datetime import datetime, timedelta, timezone


EMERGENCY_DURATION_MINUTES = 30


def create_emergency_override(reason: str) -> dict:

    now = datetime.now(timezone.utc)

    return {
        "mode": "FOUNDER_EMERGENCY_OVERRIDE",
        "reason": reason,
        "approved_by": "Founder",
        "created_at": now.isoformat(),
        "expires_at": (
            now + timedelta(minutes=EMERGENCY_DURATION_MINUTES)
        ).isoformat(),
    }


def is_emergency_active(data: dict) -> bool:

    try:
        expires_at = datetime.fromisoformat(
            data["expires_at"]
        )

        return datetime.now(timezone.utc) < expires_at

    except Exception:
        return False
