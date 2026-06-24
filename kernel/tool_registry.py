from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ToolStatus(str, Enum):
    UNKNOWN = "unknown"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


@dataclass
class ToolRecord:
    """Runtime availability record for an external tool.

    Capability answers: "Can this system conceptually do this?"
    ToolRecord answers: "Was this tool actually verified in this runtime?"
    """

    name: str
    capability: str
    status: ToolStatus = ToolStatus.UNKNOWN
    verified: bool = False
    last_checked_at: Optional[str] = None
    last_success_at: Optional[str] = None
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_available(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        checked_at = _now()
        self.status = ToolStatus.AVAILABLE
        self.verified = True
        self.last_checked_at = checked_at
        self.last_success_at = checked_at
        self.last_error = None
        if metadata:
            self.metadata.update(metadata)

    def mark_unavailable(self, error: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.status = ToolStatus.UNAVAILABLE
        self.verified = False
        self.last_checked_at = _now()
        self.last_error = error
        if metadata:
            self.metadata.update(metadata)

    def reset_unknown(self, reason: str = "not verified in current runtime") -> None:
        self.status = ToolStatus.UNKNOWN
        self.verified = False
        self.last_checked_at = _now()
        self.last_error = reason

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "capability": self.capability,
            "status": self.status.value,
            "verified": self.verified,
            "last_checked_at": self.last_checked_at,
            "last_success_at": self.last_success_at,
            "last_error": self.last_error,
            "metadata": self.metadata,
        }


@dataclass
class ToolRegistry:
    """Verified runtime tool registry for AI Kernel.

    Principle: Verification Before Assertion.
    A tool must remain UNKNOWN until a real check succeeds or fails in the
    current runtime/session.
    """

    tools: Dict[str, ToolRecord] = field(default_factory=dict)

    @classmethod
    def load_default(cls) -> "ToolRegistry":
        registry = cls()
        registry.register("github_list_files", "github.read")
        registry.register("github_read_file", "github.read")
        registry.register("github_update_file", "github.write")
        registry.register("execute_plan", "execution.plan")
        registry.register("drive_list_documents", "drive.read")
        registry.register("drive_read_document", "drive.read")
        registry.register("drive_create_document", "drive.create_doc")
        registry.register("drive_append_document", "drive.append_doc")
        registry.register("mcp_call", "mcp.call")
        return registry

    def register(self, name: str, capability: str, metadata: Optional[Dict[str, Any]] = None) -> ToolRecord:
        record = ToolRecord(name=name, capability=capability, metadata=metadata or {})
        self.tools[name] = record
        return record

    def mark_available(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> ToolRecord:
        record = self.tools.get(name) or self.register(name=name, capability="unknown")
        record.mark_available(metadata=metadata)
        return record

    def mark_unavailable(self, name: str, error: str, metadata: Optional[Dict[str, Any]] = None) -> ToolRecord:
        record = self.tools.get(name) or self.register(name=name, capability="unknown")
        record.mark_unavailable(error=error, metadata=metadata)
        return record

    def can_use(self, name: str) -> bool:
        record = self.tools.get(name)
        return bool(record and record.status == ToolStatus.AVAILABLE and record.verified)

    def require(self, name: str) -> Dict[str, Any]:
        record = self.tools.get(name)
        if not record:
            return {
                "status": "blocked",
                "reason": "tool_not_registered",
                "tool": name,
            }
        if not self.can_use(name):
            return {
                "status": "blocked",
                "reason": "tool_not_verified",
                "tool": record.as_dict(),
            }
        return {
            "status": "ok",
            "tool": record.as_dict(),
        }

    def as_dict(self) -> Dict[str, Any]:
        return {
            "tools": {name: record.as_dict() for name, record in self.tools.items()},
            "summary": self.summary(),
        }

    def summary(self) -> Dict[str, int]:
        counts = {
            "available": 0,
            "unavailable": 0,
            "unknown": 0,
        }
        for record in self.tools.values():
            counts[record.status.value] += 1
        return counts

    def verified_tools(self) -> List[str]:
        return [name for name, record in self.tools.items() if record.verified]


def load_tool_registry() -> ToolRegistry:
    return ToolRegistry.load_default()


tool_registry = load_tool_registry()
