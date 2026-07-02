from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import yaml

OWNERSHIP_PATH = Path(__file__).parent / "tool_ownership.yaml"


class ToolRoutingError(RuntimeError):
    pass


def load_tool_ownership() -> Dict[str, Any]:
    if not OWNERSHIP_PATH.exists():
        raise ToolRoutingError("living_brain/tool_ownership.yaml is required")
    data = yaml.safe_load(OWNERSHIP_PATH.read_text(encoding="utf-8")) or {}
    if data.get("owner") != "LIVING_BRAIN":
        raise ToolRoutingError("Tool ownership must belong to LIVING_BRAIN")
    return data


@dataclass(frozen=True)
class ToolRoute:
    capability: str
    owner: str
    tools: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "capability": self.capability,
            "owner": self.owner,
            "tools": self.tools,
        }


class LivingBrainToolRouter:
    """Capability-first tool router owned by LIVING_BRAIN.

    Workers must request a capability from this router instead of calling tools
    directly. This is the enforcement bridge for Brain-owned execution.
    """

    def __init__(self) -> None:
        self.ownership = load_tool_ownership()

    def capabilities(self) -> Dict[str, Any]:
        return self.ownership.get("capabilities", {})

    def resolve(self, capability: str) -> ToolRoute:
        capability = (capability or "").strip()
        entry = self.capabilities().get(capability)
        if not entry:
            raise ToolRoutingError(f"Unsupported capability: {capability}")
        owner = entry.get("owner")
        if owner != "LIVING_BRAIN":
            raise ToolRoutingError(f"Capability {capability} is not owned by LIVING_BRAIN")
        tools = entry.get("tools") or []
        if not isinstance(tools, list) or not tools:
            raise ToolRoutingError(f"Capability {capability} has no tools")
        return ToolRoute(capability=capability, owner=owner, tools=tools)

    def validate_tool_access(self, capability: str, tool: str) -> Dict[str, Any]:
        route = self.resolve(capability)
        allowed = tool in route.tools
        return {
            "status": "ok" if allowed else "blocked",
            "capability": capability,
            "tool": tool,
            "owner": route.owner,
            "allowed_tools": route.tools,
            "reason": None if allowed else "tool_not_allowed_for_capability",
        }

    def route_request(self, capability: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        route = self.resolve(capability)
        return {
            "status": "routed",
            "route": route.as_dict(),
            "payload": payload or {},
            "execution_owner": "LIVING_BRAIN",
        }


tool_router = LivingBrainToolRouter()
