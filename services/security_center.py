from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SecurityCenter:
    """Trung tâm bảo mật của Trung Huyền OS."""

    HIGH_RISK_ACTIONS = {
        "delete",
        "batch_delete",
        "deploy",
        "change_secret",
        "grant_permission",
        "repository_mass_refactor",
    }

    def __init__(self) -> None:
        self.audit_log: List[Dict[str, Any]] = []
        self.permissions: Dict[str, List[str]] = {
            "ai_ceo": ["plan", "dispatch", "review", "approve_medium"],
            "runtime_director": ["execute", "verify", "rollback"],
            "ciso": ["approve_high", "block", "audit", "recover"],
            "developer_runtime": ["patch", "commit", "verify"],
        }

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "service": "security_center",
            "permission_subjects": sorted(self.permissions.keys()),
            "audit_count": len(self.audit_log),
        }

    def check_permission(self, subject: str, action: str) -> Dict[str, Any]:
        allowed = action in self.permissions.get(subject, [])
        decision = {
            "status": "allowed" if allowed else "blocked",
            "subject": subject,
            "action": action,
            "checked_at": now(),
        }
        self.audit(subject=subject, action=f"permission.{action}", result=decision["status"], detail=decision)
        return decision

    def assess_risk(self, action: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        risk = "high" if action in self.HIGH_RISK_ACTIONS else "medium" if action.startswith("update") else "low"
        if payload.get("operation_count", 0) > 20:
            risk = "high"
        decision = {
            "status": "ok",
            "action": action,
            "risk": risk,
            "requires_approval": risk in {"medium", "high"},
            "assessed_at": now(),
        }
        self.audit("security_center", f"risk.{action}", risk, decision)
        return decision

    def audit(self, subject: str, action: str, result: str, detail: Dict[str, Any] | None = None) -> Dict[str, Any]:
        record = {
            "subject": subject,
            "action": action,
            "result": result,
            "detail": detail or {},
            "created_at": now(),
        }
        self.audit_log.append(record)
        return {"status": "logged", "record": record}

    def recent_audit(self, limit: int = 50) -> Dict[str, Any]:
        return {"status": "ok", "records": self.audit_log[-limit:]}


security_center = SecurityCenter()
