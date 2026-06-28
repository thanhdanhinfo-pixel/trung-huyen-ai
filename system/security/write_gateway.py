from typing import Any, Dict

from services.github_runtime import github_runtime
from system.security.audit import write_audit, require_audit
from system.security.grant_manager import is_founder_grant_active
from system.security.unlock import is_system_unlocked


ACTOR = "TRUNG_HUYEN_AI_OS"
PLACEHOLDER_MARKERS = (
    "<dán lại",
    "<dan lai",
    "placeholder",
    "TODO",
)
MAX_SIZE_DROP_RATIO = 0.30


def _is_authorized(founder_grant: Dict[str, Any]) -> bool:
    """RULE-019: Unified unlock is the primary authority.

    Founder Grant remains supported for compatibility and for external calls that
    pass a persistent grant token through MCP.
    """
    if is_system_unlocked():
        return True

    return is_founder_grant_active(
        founder_grant,
        subject=ACTOR,
        min_level=3,
        scope="ALL_SYSTEM",
    )


def _write_safety_check(target: str, old_content: str, new_content: str) -> Dict[str, Any]:
    """RULE-020: WRITE_SAFETY_GATE.

    Prevent accidental destructive full-file overwrites.
    """
    stripped = (new_content or "").strip()
    if not stripped:
        return {
            "status": "error",
            "message": "WRITE_SAFETY_GATE blocked empty content",
            "target": target,
        }

    lowered = stripped.lower()
    for marker in PLACEHOLDER_MARKERS:
        if marker.lower() in lowered:
            return {
                "status": "error",
                "message": f"WRITE_SAFETY_GATE blocked placeholder content: {marker}",
                "target": target,
            }

    old_size = len(old_content or "")
    new_size = len(new_content or "")
    if old_size > 0 and new_size < old_size * (1 - MAX_SIZE_DROP_RATIO):
        return {
            "status": "error",
            "message": "WRITE_SAFETY_GATE blocked abnormal size reduction",
            "target": target,
            "old_size": old_size,
            "new_size": new_size,
        }

    return {"status": "ok"}


def system_write(
    action: str,
    target: str,
    payload: Dict[str, Any],
    founder_grant: Dict[str, Any],
) -> Dict[str, Any]:

    if not _is_authorized(founder_grant):
        return {
            "status": "error",
            "message": "System is locked. Unified unlock or Founder grant required.",
        }

    audit = write_audit(
        "system_write",
        {
            "approved_by": founder_grant.get("granted_by"),
            "approval_id": founder_grant.get("session_id") or founder_grant.get("token"),
            "actor": ACTOR,
            "action": action,
            "target": target,
            "status": "pending",
        },
    )

    if not require_audit(audit):
        return {
            "status": "error",
            "message": "audit validation failed",
        }

    if action == "update_file":
        current = github_runtime.read_file(target)
        old_content = current.get("content", "")
        new_content = payload.get("content", "")

        safety = _write_safety_check(target, old_content, new_content)
        if safety.get("status") != "ok":
            return safety

        return github_runtime.update_file(
            path=target,
            content=new_content,
            message=payload.get("message", "system write update"),
            sha=payload.get("sha") or current.get("sha"),
        )

    if action == "patch_file":
        current = github_runtime.read_file(target)
        content = current.get("content", "")
        find = payload.get("find", "")
        replace = payload.get("replace", "")

        if not find or find not in content:
            return {
                "status": "error",
                "message": "find text not found",
            }

        new_content = content.replace(find, replace, 1)
        safety = _write_safety_check(target, content, new_content)
        if safety.get("status") != "ok":
            return safety

        return github_runtime.update_file(
            path=target,
            content=new_content,
            message=payload.get("message", "system write patch"),
            sha=current.get("sha"),
        )

    if action == "move_file":
        return github_runtime.move_file(
            source=target,
            destination=payload.get("destination", ""),
            message=payload.get("message", "system write move"),
        )

    return {
        "status": "error",
        "message": f"Unsupported system_write action: {action}",
    }
