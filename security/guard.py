from __future__ import annotations

from security.dual_approval import ensure_approved
from security.emergency_mode import ensure_action_allowed
from security.high_risk_audit import write_high_risk_audit


def pre_execute(action_name: str, payload: dict | None = None, approved: bool = False) -> None:
    ensure_action_allowed(action_name)
    ensure_approved(action_name, approved=approved)
    write_high_risk_audit(
        action_name=action_name,
        payload=payload or {},
        result={"status": "started"},
        mode="pre_execute",
    )
