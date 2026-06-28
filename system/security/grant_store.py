import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

try:
    from google.cloud import firestore
except Exception:
    firestore = None


STORE_PATH = Path("runtime/state/founder_grants.json")
COLLECTION = "system_founder_grants"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _firestore_ref(token: str):
    if firestore is None:
        return None
    try:
        client = firestore.Client()
        return client.collection(COLLECTION).document(token)
    except Exception:
        return None


def _ensure_store():
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not STORE_PATH.exists():
        STORE_PATH.write_text(json.dumps({}, indent=2), encoding="utf-8")


def _load():
    _ensure_store()
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save(data):
    STORE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_local(token: str, grant: dict) -> None:
    data = _load()
    data[token] = grant
    _save(data)


def _load_local(token: str):
    return _load().get(token)


def create_grant(grant: dict) -> str:
    token = str(uuid.uuid4())
    grant["token"] = token
    grant["created_at"] = grant.get("created_at") or _now()
    grant["updated_at"] = _now()

    ref = _firestore_ref(token)
    if ref is not None:
        try:
            ref.set(grant)
            return token
        except Exception:
            pass

    _save_local(token, grant)
    return token


def load_grant(token: str):
    if not token:
        return None

    ref = _firestore_ref(token)
    if ref is not None:
        try:
            doc = ref.get()
            if doc.exists:
                return doc.to_dict()
        except Exception:
            pass

    return _load_local(token)


def revoke_grant(token: str, reason: str = "manual revoke"):
    grant = load_grant(token)
    if not grant:
        return False

    grant["status"] = "revoked"
    grant["revoked_at"] = _now()
    grant["revoke_reason"] = reason
    grant["updated_at"] = _now()

    ref = _firestore_ref(token)
    if ref is not None:
        try:
            ref.set(grant)
            return True
        except Exception:
            pass

    _save_local(token, grant)
    return True


def complete_grant(token: str, reason: str = "task completed"):
    grant = load_grant(token)
    if not grant:
        return False

    grant["status"] = "completed"
    grant["completed_at"] = _now()
    grant["complete_reason"] = reason
    grant["updated_at"] = _now()

    ref = _firestore_ref(token)
    if ref is not None:
        try:
            ref.set(grant)
            return True
        except Exception:
            pass

    _save_local(token, grant)
    return True
