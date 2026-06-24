from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .relationship import RelationshipType, SystemRelationship
from .system_node import NodeStatus, NodeType, SystemNode


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DiscoveryResult:
    """Result of one system discovery scan."""

    status: str
    discovered_at: str = field(default_factory=utc_now)
    nodes: List[SystemNode] = field(default_factory=list)
    relationships: List[SystemRelationship] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "discovered_at": self.discovered_at,
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "nodes": [node.to_dict() for node in self.nodes],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "warnings": self.warnings,
        }


@dataclass
class DiscoveryEngine:
    """System discovery layer for AI Kernel.

    Discovery turns repository/runtime observations into SystemNode and
    SystemRelationship objects. It is the bridge from real system state to the
    Kernel Digital Twin.
    """

    last_result: DiscoveryResult | None = None

    def discover_from_paths(self, paths: Iterable[str]) -> DiscoveryResult:
        nodes: Dict[str, SystemNode] = {}
        relationships: List[SystemRelationship] = []

        for path in sorted(set(paths)):
            if not path:
                continue
            node = self._node_from_path(path)
            nodes[node.id] = node

            owner_id = self._owner_for_path(path)
            if owner_id and owner_id != node.id:
                relationships.append(
                    SystemRelationship(
                        source=owner_id,
                        target=node.id,
                        relation=RelationshipType.OWNS,
                        description=f"{owner_id} owns discovered module {node.id}.",
                        metadata={"source": "discovery.path", "path": path},
                    )
                )

        result = DiscoveryResult(
            status="ok",
            nodes=list(nodes.values()),
            relationships=relationships,
        )
        self.last_result = result
        return result

    def apply_to_model(self, system_model: Any, result: DiscoveryResult | None = None) -> Dict[str, Any]:
        result = result or self.last_result
        if not result:
            return {"status": "error", "message": "No discovery result available."}

        for node in result.nodes:
            system_model.add_node(node)
        for relationship in result.relationships:
            system_model.add_relationship(relationship)

        return {
            "status": "ok",
            "applied_nodes": len(result.nodes),
            "applied_relationships": len(result.relationships),
            "system_summary": system_model.summary(),
        }

    def _node_from_path(self, path: str) -> SystemNode:
        node_id = self._path_to_node_id(path)
        node_type = self._classify_path(path)
        owner = self._owner_for_path(path) or "repository"

        return SystemNode(
            id=node_id,
            name=path,
            node_type=node_type,
            role=self._role_for_path(path, node_type),
            owner=owner,
            description=f"Discovered repository artifact: {path}",
            status=NodeStatus.DISCOVERED,
            lifecycle="discovered",
            metadata={"path": path, "source": "repository"},
        )

    def _path_to_node_id(self, path: str) -> str:
        normalized = path.strip("/").replace("/", ".")
        if normalized.endswith(".py"):
            normalized = normalized[:-3]
        return normalized or "repository"

    def _classify_path(self, path: str) -> NodeType:
        if path.startswith("kernel/"):
            return NodeType.KERNEL_COMPONENT
        if path.startswith("worker/") or "agent" in path:
            return NodeType.AGENT
        if path.startswith("api/") or path.startswith("services/"):
            return NodeType.SERVICE
        if path.startswith("knowledge/") or path.endswith(".md"):
            return NodeType.KNOWLEDGE
        if path.startswith("static/") or path.startswith("docs/"):
            return NodeType.RESOURCE
        return NodeType.SERVICE if path.endswith(".py") else NodeType.RESOURCE

    def _owner_for_path(self, path: str) -> str:
        if path.startswith("kernel/"):
            return "kernel"
        if path.startswith("worker/"):
            return "kernel.runtime"
        if path.startswith("api/"):
            return "api"
        if path.startswith("services/"):
            return "service_layer"
        if path.startswith("knowledge/"):
            return "kernel.memory"
        return "repository"

    def _role_for_path(self, path: str, node_type: NodeType) -> str:
        if path.startswith("kernel/"):
            return "Kernel component discovered from repository."
        if path.startswith("api/"):
            return "HTTP API surface for AI OS."
        if path.startswith("worker/"):
            return "Worker execution runtime."
        if "planner" in path:
            return "Planning capability."
        if "execution" in path or "execute" in path:
            return "Execution capability."
        return f"Discovered {node_type.value} artifact."


def load_discovery_engine() -> DiscoveryEngine:
    return DiscoveryEngine()


discovery_engine = load_discovery_engine()
