from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class GovernanceRule:
    """A rule or principle used by the AI Kernel to make decisions."""

    code: str
    title: str
    description: str
    level: str = "principle"
    enabled: bool = True
    created_at: str = field(default_factory=_now)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "title": self.title,
            "description": self.description,
            "level": self.level,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }


@dataclass
class KernelGovernance:
    """Governance layer of the AI Kernel.

    This answers the Kernel question:
    "Which principles and rules should guide my decisions?"
    """

    rules: List[GovernanceRule] = field(default_factory=list)

    def add_rule(self, code: str, title: str, description: str, level: str = "principle", enabled: bool = True) -> GovernanceRule:
        rule = GovernanceRule(
            code=code,
            title=title,
            description=description,
            level=level,
            enabled=enabled,
        )
        self.rules.append(rule)
        return rule

    def active_rules(self) -> List[GovernanceRule]:
        return [rule for rule in self.rules if rule.enabled]

    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an action against Kernel governance.

        This first version is conservative and focuses on refactor safety.
        """
        issues: List[Dict[str, Any]] = []
        action_type = action.get("type", "")
        target = action.get("target", "")
        approved = bool(action.get("approved", False))

        if action_type in {"write", "delete", "deploy", "execute_plan"} and not approved:
            issues.append({
                "level": "error",
                "code": "APPROVAL_REQUIRED",
                "message": "Write/delete/deploy/execute actions require explicit approval.",
            })

        if "legacy" in str(target).lower() and action_type in {"delete", "rewrite"}:
            issues.append({
                "level": "warning",
                "code": "LEGACY_MIGRATION_GUARD",
                "message": "Legacy cleanup should happen only after Kernel migration is stable.",
            })

        return {
            "status": "ok" if not any(i["level"] == "error" for i in issues) else "blocked",
            "issues": issues,
            "action": action,
        }

    def as_dict(self) -> Dict[str, Any]:
        return {
            "rule_count": len(self.rules),
            "active_rule_count": len(self.active_rules()),
            "rules": [rule.as_dict() for rule in self.rules],
        }

    def seed_foundation_governance(self) -> None:
        if self.rules:
            return

        self.add_rule(
            code="KERNEL_FIRST",
            title="Kernel-first architecture",
            description="New AI OS V2 capabilities should route through AI Kernel instead of creating isolated state owners.",
        )
        self.add_rule(
            code="PARALLEL_REFACTOR",
            title="Build V2 beside legacy",
            description="Build Kernel V2 in parallel with the legacy system. Migrate only after the new path is stable.",
        )
        self.add_rule(
            code="NO_DUPLICATE_MODULES",
            title="Avoid duplicate architecture",
            description="Do not create new modules that duplicate existing responsibilities unless migration requires an adapter.",
        )
        self.add_rule(
            code="APPROVAL_FOR_WRITE",
            title="Approval required for side effects",
            description="Actions that write, delete, deploy or execute plans must require explicit approval.",
            level="policy",
        )


def load_governance() -> KernelGovernance:
    governance = KernelGovernance()
    governance.seed_foundation_governance()
    return governance


governance = load_governance()
