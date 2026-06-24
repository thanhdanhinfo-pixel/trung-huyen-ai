from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NodeType(str, Enum):
    """Ontology type for every entity in TRUNG_HUYEN_AI_OS."""

    KERNEL = "kernel"
    KERNEL_COMPONENT = "kernel_component"
    AGENT = "agent"
    SERVICE = "service"
    RESOURCE = "resource"
    WORKFLOW = "workflow"
    KNOWLEDGE = "knowledge"
    TOOL = "tool"
    EXTERNAL = "external"


class NodeStatus(str, Enum):
    """Runtime/model status of a system node."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCOVERED = "discovered"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"


@dataclass
class SystemNode:
    """A node in the AI OS Digital Twin.

    SystemNode is the common language used by the Kernel to describe every
    important part of the system: Kernel components, agents, services,
    resources, tools, workflows and knowledge objects.

    This is not a Python-file model. It is a system-understanding model.
    """

    id: str
    name: str
    node_type: NodeType
    role: str
    owner: str
    description: str = ""
    status: NodeStatus = NodeStatus.UNKNOWN
    lifecycle: str = "development"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def add_dependency(self, node_id: str) -> None:
        if node_id and node_id not in self.dependencies:
            self.dependencies.append(node_id)
            self.updated_at = utc_now()

    def add_capability(self, capability: str) -> None:
        if capability and capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = utc_now()

    def update_status(self, status: NodeStatus) -> None:
        self.status = status
        self.updated_at = utc_now()

    def update_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
        self.updated_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "role": self.role,
            "owner": self.owner,
            "description": self.description,
            "status": self.status.value,
            "lifecycle": self.lifecycle,
            "capabilities": list(self.capabilities),
            "dependencies": list(self.dependencies),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemNode":
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=NodeType(data["type"]),
            role=data.get("role", ""),
            owner=data.get("owner", ""),
            description=data.get("description", ""),
            status=NodeStatus(data.get("status", NodeStatus.UNKNOWN.value)),
            lifecycle=data.get("lifecycle", "development"),
            capabilities=list(data.get("capabilities", [])),
            dependencies=list(data.get("dependencies", [])),
            metadata=dict(data.get("metadata", {})),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
