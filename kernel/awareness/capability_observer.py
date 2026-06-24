from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CapabilitySnapshot:
    observed_at: str = field(default_factory=now)
    status: str = "unknown"
    designed_capabilities: Dict[str, Any] = field(default_factory=dict)
    verified_tools: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observed_at": self.observed_at,
            "status": self.status,
            "designed_capabilities": self.designed_capabilities,
            "verified_tools": self.verified_tools,
            "summary": self.summary,
            "warnings": self.warnings,
        }


class CapabilityObserver:
    """Observe designed and runtime-verified capabilities.

    Capability answers: what the system is designed to do.
    ToolRegistry answers: what has actually been verified in this runtime.
    This observer compares both views for Kernel self-awareness.
    """

    def observe(self, kernel: Any) -> CapabilitySnapshot:
        warnings: List[Dict[str, Any]] = []

        designed = {}
        if hasattr(kernel, "capabilities"):
            designed = kernel.capabilities.summary()

        verified_tools: List[str] = []
        tool_summary: Dict[str, Any] = {"available": 0, "unavailable": 0, "unknown": 0}
        tool_registry = getattr(kernel, "tool_registry", None)
        if tool_registry:
            verified_tools = tool_registry.verified_tools()
            tool_summary = tool_registry.summary()
        else:
            warnings.append({
                "code": "MISSING_TOOL_REGISTRY",
                "level": "warning",
                "message": "Kernel has no ToolRegistry; runtime tool availability cannot be verified.",
            })

        return CapabilitySnapshot(
            status="ok" if not warnings else "warning",
            designed_capabilities=designed,
            verified_tools=verified_tools,
            summary={
                "designed": designed,
                "tools": tool_summary,
            },
            warnings=warnings,
        )


capability_observer = CapabilityObserver()
