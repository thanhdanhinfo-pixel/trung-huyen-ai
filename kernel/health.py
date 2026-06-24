from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HealthIssue:
    code: str
    message: str
    level: str = "warning"
    source: str = "kernel"
    created_at: str = field(default_factory=_now)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level,
            "source": self.source,
            "created_at": self.created_at,
        }


@dataclass
class KernelHealth:
    """Health layer of the AI Kernel.

    This answers the Kernel question:
    "What is the current health of the AI OS?"
    """

    issues: List[HealthIssue] = field(default_factory=list)
    checked_at: str = field(default_factory=_now)

    def check(self, kernel: Any) -> Dict[str, Any]:
        self.issues = []
        self.checked_at = _now()

        self._check_identity(kernel)
        self._check_registry(kernel)
        self._check_runtime(kernel)
        self._check_capabilities(kernel)
        self._check_memory(kernel)
        self._check_governance(kernel)

        return self.report()

    def _check_identity(self, kernel: Any) -> None:
        identity = getattr(kernel, "identity", None)
        if not identity:
            self.issues.append(HealthIssue("MISSING_IDENTITY", "Kernel identity is missing.", "error", "identity"))

    def _check_registry(self, kernel: Any) -> None:
        registry = getattr(kernel, "registry", None)
        if not registry:
            self.issues.append(HealthIssue("MISSING_REGISTRY", "Kernel registry is missing.", "error", "registry"))
            return
        validation = registry.validate()
        for issue in validation.get("issues", []):
            self.issues.append(
                HealthIssue(
                    code=issue.get("code", "REGISTRY_ISSUE"),
                    message=issue.get("message", "Registry issue."),
                    level=issue.get("level", "warning"),
                    source="registry",
                )
            )

    def _check_runtime(self, kernel: Any) -> None:
        runtime = getattr(kernel, "runtime", None)
        if not runtime:
            self.issues.append(HealthIssue("MISSING_RUNTIME", "Kernel runtime is missing.", "error", "runtime"))
            return
        snapshot = runtime.snapshot()
        if snapshot.get("failed_count", 0) > 0:
            self.issues.append(HealthIssue("FAILED_TASKS_PRESENT", "Runtime has failed tasks.", "warning", "runtime"))

    def _check_capabilities(self, kernel: Any) -> None:
        capabilities = getattr(kernel, "capabilities", None)
        if not capabilities:
            self.issues.append(HealthIssue("MISSING_CAPABILITIES", "Kernel capabilities are missing.", "error", "capability"))
            return
        validation = capabilities.validate()
        if validation.get("disabled_count", 0) > 0:
            self.issues.append(HealthIssue("DISABLED_CAPABILITIES", "Some capabilities are disabled or unverified.", "info", "capability"))

    def _check_memory(self, kernel: Any) -> None:
        memory = getattr(kernel, "memory", None)
        if not memory:
            self.issues.append(HealthIssue("MISSING_MEMORY", "Kernel memory is missing.", "error", "memory"))
            return
        if memory.as_dict().get("record_count", 0) == 0:
            self.issues.append(HealthIssue("EMPTY_MEMORY", "Kernel memory has no foundation records.", "warning", "memory"))

    def _check_governance(self, kernel: Any) -> None:
        governance = getattr(kernel, "governance", None)
        if not governance:
            self.issues.append(HealthIssue("MISSING_GOVERNANCE", "Kernel governance is missing.", "error", "governance"))
            return
        if governance.as_dict().get("active_rule_count", 0) == 0:
            self.issues.append(HealthIssue("NO_ACTIVE_GOVERNANCE_RULES", "No active governance rules.", "warning", "governance"))

    def score(self) -> int:
        score = 100
        for issue in self.issues:
            if issue.level == "error":
                score -= 30
            elif issue.level == "warning":
                score -= 10
            elif issue.level == "info":
                score -= 2
        return max(score, 0)

    def report(self) -> Dict[str, Any]:
        issue_dicts = [issue.as_dict() for issue in self.issues]
        has_error = any(issue.get("level") == "error" for issue in issue_dicts)
        return {
            "status": "error" if has_error else "ok",
            "score": self.score(),
            "checked_at": self.checked_at,
            "issue_count": len(issue_dicts),
            "issues": issue_dicts,
        }


def load_health() -> KernelHealth:
    return KernelHealth()


health = load_health()
