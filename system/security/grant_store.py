import json
import uuid
from pathlib import Path
from datetime import datetime, timezone


STORE_PATH = Path("runtime/state/founder_grants.json")


def _ensure_store():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not STORE_PATH.exists():
        STORE_PATH.write_text(
            json.dumps({}, indent=2),
            encoding="utf-8",
        )


def _load():
    _ensure_store()

    return json.loads(
        STORE_PATH.read_text(encoding="utf-8")
    )


def _save(data):
    STORE_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_grant(grant: dict) -> str:
    data = _load()

    token = str(uuid.uuid4())

    grant["token"] = token
    grant["created_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    data[token] = grant

    _save(data)

    return token


def load_grant(token: str):
    data = _load()

    return data.get(token)


def revoke_grant(
    token: str,
    reason: str = "manual revoke",
):
    data = _load()

    grant = data.get(token)

    if not grant:
        return False

    grant["status"] = "revoked"
    grant["revoked_at"] = datetime.now(
        timezone.utc
    ).isoformat()
    grant["revoke_reason"] = reason

    data[token] = grant

    _save(data)

    return True


def complete_grant(
    token: str,
    reason: str = "task completed",
):
    data = _load()

    grant = data.get(token)

    if not grant:
        return False

    grant["status"] = "completed"
    grant["completed_at"] = datetime.now(
        timezone.utc
    ).isoformat()
    grant["complete_reason"] = reason

    data[token] = grant

    _save(data)

    return True
