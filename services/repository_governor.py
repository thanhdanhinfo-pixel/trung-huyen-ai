from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


PROTECTED_ROOT_FILES = {
    "app.py",
    "config.py",
    "Dockerfile",
    "requirements.txt",
    "README.md",
    ".gitignore",
}

PROTECTED_PREFIXES = {
    "api/",
    "services/",
}

ALLOWED_TARGET_PREFIXES = {
    "core/",
    "brain/",
    "organization/",
    "runtime/",
    "security/",
    "monitoring/",
    "memory/",
    "knowledge/",
    "connectors/",
    "api/",
    "docs/",
    "tests/",
    "scripts/",
    "services/",
}


@dataclass
class PolicyDecision:
    allowed: bool
    risk: str
    reasons: List[str] = field(default_factory=list)
    operation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepositoryGovernor:
    """Bộ kiểm soát an toàn cho mọi thay đổi cấu trúc repository.

    Mục tiêu: không cho phép refactor ồ ạt, không động vào file lõi nếu chưa có
    chính sách riêng, và không cho phép di chuyển ra ngoài kiến trúc Trung Huyền OS.
    """

    def assess_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        op_type = operation.get("type")
        if op_type == "move":
            return self._assess_move(operation).to_dict()
        if op_type == "delete":
            return self._assess_delete(operation).to_dict()
        return PolicyDecision(
            allowed=False,
            risk="high",
            reasons=[f"Loại thao tác chưa được hỗ trợ: {op_type}"],
            operation=operation,
        ).to_dict()

    def assess_plan(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        decisions = [self.assess_operation(op) for op in operations]
        blocked = [item for item in decisions if not item.get("allowed")]
        high_risk = [item for item in decisions if item.get("risk") == "high"]
        return {
            "status": "approved" if not blocked else "blocked",
            "operation_count": len(operations),
            "blocked_count": len(blocked),
            "high_risk_count": len(high_risk),
            "decisions": decisions,
        }

    def _assess_move(self, operation: Dict[str, Any]) -> PolicyDecision:
        source = operation.get("source", "")
        destination = operation.get("destination", "")
        reasons: List[str] = []
        risk = "low"

        if not source or not destination:
            return PolicyDecision(False, "high", ["Thiếu source hoặc destination"], operation)

        if source in PROTECTED_ROOT_FILES:
            reasons.append(f"File lõi được bảo vệ, không di chuyển trong batch tự động: {source}")
            risk = "high"

        if any(source.startswith(prefix) for prefix in PROTECTED_PREFIXES):
            reasons.append(f"Nguồn thuộc vùng đã có cấu trúc, cần review thủ công: {source}")
            risk = "medium"

        if not any(destination.startswith(prefix) for prefix in ALLOWED_TARGET_PREFIXES):
            reasons.append(f"Đích không thuộc kiến trúc chuẩn: {destination}")
            risk = "high"

        if destination == source:
            reasons.append("Source và destination trùng nhau")
            risk = "high"

        allowed = risk != "high"
        if allowed and not reasons:
            reasons.append("Được phép theo chính sách hiện tại")

        return PolicyDecision(allowed, risk, reasons, operation)

    def _assess_delete(self, operation: Dict[str, Any]) -> PolicyDecision:
        path = operation.get("path", "")
        if not path:
            return PolicyDecision(False, "high", ["Thiếu path"], operation)
        if path in PROTECTED_ROOT_FILES:
            return PolicyDecision(False, "high", [f"Không được xóa file lõi: {path}"], operation)
        if path.endswith(".pyc") or path.startswith("__pycache__"):
            return PolicyDecision(True, "low", ["File sinh tự động, được phép xóa"], operation)
        if path.endswith(".md") and (path.startswith("docs/") or path.startswith("archive/")):
            return PolicyDecision(True, "low", ["Tài liệu trong vùng quản lý, được phép xóa khi có plan"], operation)
        return PolicyDecision(False, "medium", ["Xóa file cần review thủ công"], operation)


repository_governor = RepositoryGovernor()
