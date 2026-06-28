from datetime import datetime, timezone

try:
    from google.cloud import firestore
except Exception:  # pragma: no cover - local/dev fallback
    firestore = None

UNLOCK_MODE = "FOUNDER_UNLOCK_MODE"
REGISTERED_LOCKS = []
UNLOCK_COLLECTION = "system_runtime"
UNLOCK_DOCUMENT = "unlock_state"
_SYSTEM_UNLOCK_STATE = {
    "active": False,
    "reason": "",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _firestore_ref():
    if firestore is None:
        return None
    try:
        return firestore.Client().collection(UNLOCK_COLLECTION).document(UNLOCK_DOCUMENT)
    except Exception:
        return None


def _save_unlock_state(active: bool, reason: str) -> None:
    _SYSTEM_UNLOCK_STATE["active"] = active
    _SYSTEM_UNLOCK_STATE["reason"] = reason

    ref = _firestore_ref()
    if ref is None:
        return

    try:
        ref.set(
            {
                "active": active,
                "reason": reason,
                "updated_at": _now(),
                "mode": UNLOCK_MODE,
                "approved_by": "Founder",
            },
            merge=True,
        )
    except Exception:
        return


def _load_unlock_state() -> dict:
    ref = _firestore_ref()
    if ref is None:
        return _SYSTEM_UNLOCK_STATE

    try:
        doc = ref.get()
        if doc.exists:
            data = doc.to_dict() or {}
            _SYSTEM_UNLOCK_STATE["active"] = bool(data.get("active", False))
            _SYSTEM_UNLOCK_STATE["reason"] = data.get("reason", "")
    except Exception:
        pass

    return _SYSTEM_UNLOCK_STATE


def register_lock(handler=None, *, name: str = "", description: str = ""):
    """Register a lock adapter for RULE-019 unified unlock.

    New lock layers must register here instead of requiring Founder to open a
    separate hidden lock manually.
    """
    def _register(func):
        func.lock_name = name or getattr(func, "__name__", "unknown_lock")
        func.lock_description = description
        REGISTERED_LOCKS.append(func)
        return func

    if handler is not None:
        return _register(handler)

    return _register


def list_registered_locks() -> list:
    return [
        {
            "name": getattr(handler, "lock_name", getattr(handler, "__name__", "unknown_lock")),
            "description": getattr(handler, "lock_description", ""),
        }
        for handler in REGISTERED_LOCKS
    ]


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
        "created_at": _now(),
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
    _save_unlock_state(True, reason)

    unlock = create_founder_unlock(
        level=5,
        reason=reason,
        session_id="UNIFIED-UNLOCK",
    )

    results = []
    for handler in REGISTERED_LOCKS:
        lock_name = getattr(handler, "lock_name", getattr(handler, "__name__", "unknown_lock"))
        try:
            result = handler()
            if isinstance(result, dict):
                results.append({"lock": lock_name, **result})
            else:
                results.append({"lock": lock_name, "status": "ok", "result": result})
        except Exception as exc:
            results.append({"lock": lock_name, "status": "error", "error": str(exc)})

    return {
        "status": "ok",
        "unlock": unlock,
        "locks_opened": len(results),
        "registered_locks": list_registered_locks(),
        "results": results,
        "persistent": _firestore_ref() is not None,
    }


def close_all_locks(reason: str = "Founder command") -> dict:
    _save_unlock_state(False, reason)
    return {
        "status": "ok",
        "active": False,
        "reason": reason,
        "persistent": _firestore_ref() is not None,
    }


def is_system_unlocked() -> bool:
    state = _load_unlock_state()
    return bool(state.get("active", False))


@register_lock(name="founder_grant", description="Persistent Founder Grant authority layer")
def _open_founder_grant_layer() -> dict:
    return {"status": "ok", "mode": "persistent_grant_store"}


@register_lock(name="system_write", description="System write authorization layer")
def _open_system_write_layer() -> dict:
    return {"status": "ok", "mode": "unified_unlock_authorized"}


@register_lock(name="audit", description="Audit/logging layer; log-only and non-blocking")
def _open_audit_layer() -> dict:
    return {"status": "ok", "mode": "non_blocking_log"}


@register_lock(name="write_safety_gate", description="Write safety remains active while unlocked")
def _open_write_safety_gate_layer() -> dict:
    return {"status": "ok", "mode": "safety_gate_active"}


@register_lock(name="future_lock_registry", description="Future lock layers must register through register_lock")
def _open_future_lock_registry_layer() -> dict:
    return {"status": "ok", "mode": "registry_ready"}
