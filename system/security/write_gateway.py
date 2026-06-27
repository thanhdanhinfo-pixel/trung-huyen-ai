from typing import Any, Dict

from services.github_runtime import github_runtime
from system.security.audit import write_audit, require_audit
from system.security.grant_manager import is_founder_grant_active


ACTOR = "TRUNG_HUYEN_AI_OS"


def system_write(
    action: str,
    target: str,
    payload: Dict[str, Any],
    founder_grant: Dict[str, Any],
) -> Dict[str, Any]:

    if not is_founder_grant_active(
        founder_grant,
        subject=ACTOR,
        min_level=3,
        scope="ALL_SYSTEM",
    ):
        return {
            "status": "error",
            "message": "System is locked. Founder grant required.",
        }

    audit = write_audit(
        "system_write",
        {
            "approved_by": founder_grant.get("granted_by"),
            "approval_id": founder_grant.get("session_id"),
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
        return github_runtime.update_file(
            path=target,
            content=payload.get("content", ""),
            message=payload.get("message", "system write update"),
            sha=payload.get("sha"),
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

        return github_runtime.update_file(
            path=target,
            content=content.replace(find, replace, 1),
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
