from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .relationship import RelationshipType, SystemRelationship
from .system_node import NodeStatus, NodeType, SystemNode


@dataclass
class SystemModel:
    """Digital Twin of TRUNG_HUYEN_AI_OS.

    This model is the Kernel's internal understanding of the system.
    It answers:
    - What components exist?
    - Who owns what?
    - What depends on what?
    - What is impacted if a component changes?
    """

    nodes: Dict[str, SystemNode] = field(default_factory=dict)
    relationships: List[SystemRelationship] = field(default_factory=list)

    def add_node(self, node: SystemNode) -> SystemNode:
        self.nodes[node.id] = node
        return node

    def add_relationship(self, relationship: SystemRelationship) -> SystemRelationship:
        self.relationships.append(relationship)
        return relationship

    def get_node(self, node_id: str) -> Optional[SystemNode]:
        return self.nodes.get(node_id)

    def find_nodes_by_type(self, node_type: NodeType) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self.nodes.values() if node.node_type == node_type]

    def dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        targets = [
            rel.target
            for rel in self.relationships
            if rel.source == node_id and rel.relation in {RelationshipType.DEPENDS_ON, RelationshipType.USES}
        ]
        return [self.nodes[target].to_dict() for target in targets if target in self.nodes]

    def dependents(self, node_id: str) -> List[Dict[str, Any]]:
        sources = [
            rel.source
            for rel in self.relationships
            if rel.target == node_id and rel.relation in {RelationshipType.DEPENDS_ON, RelationshipType.USES}
        ]
        return [self.nodes[source].to_dict() for source in sources if source in self.nodes]

    def owned_by(self, owner: str) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self.nodes.values() if node.owner == owner]

    def impact(self, node_id: str) -> Dict[str, Any]:
        return {
            "node": self.nodes[node_id].to_dict() if node_id in self.nodes else None,
            "direct_dependents": self.dependents(node_id),
            "direct_dependencies": self.dependencies(node_id),
        }

    def relationships_for(self, node_id: str) -> List[Dict[str, Any]]:
        return [
            rel.to_dict()
            for rel in self.relationships
            if rel.source == node_id or rel.target == node_id
        ]

    def summary(self) -> Dict[str, Any]:
        by_type: Dict[str, int] = {}
        by_status: Dict[str, int] = {}

        for node in self.nodes.values():
            by_type[node.node_type.value] = by_type.get(node.node_type.value, 0) + 1
            by_status[node.status.value] = by_status.get(node.status.value, 0) + 1

        return {
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "by_type": by_type,
            "by_status": by_status,
        }

    def export(self) -> Dict[str, Any]:
        return {
            "summary": self.summary(),
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "relationships": [relationship.to_dict() for relationship in self.relationships],
        }


def build_foundation_system_model() -> SystemModel:
    """Build the first Kernel-first Digital Twin foundation."""
    model = SystemModel()

    model.add_node(SystemNode(
        id="kernel",
        name="AI Kernel",
        node_type=NodeType.KERNEL,
        role="Central system intelligence and coordination layer",
        owner="TRUNG_HUYEN_AI_OS",
        status=NodeStatus.ACTIVE,
        lifecycle="v2_foundation",
    ))
    model.add_node(SystemNode(
        id="kernel.runtime",
        name="Kernel Runtime",
        node_type=NodeType.KERNEL_COMPONENT,
        role="Owns runtime state, ticks and task queue",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="kernel.memory",
        name="Kernel Memory",
        node_type=NodeType.KERNEL_COMPONENT,
        role="Stores decisions, lessons and architecture knowledge",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="kernel.governance",
        name="Kernel Governance",
        node_type=NodeType.KERNEL_COMPONENT,
        role="Validates decisions and actions against principles",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="kernel.capability",
        name="Kernel Capability",
        node_type=NodeType.KERNEL_COMPONENT,
        role="Describes designed system capabilities",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="kernel.tool_registry",
        name="Kernel Tool Registry",
        node_type=NodeType.KERNEL_COMPONENT,
        role="Tracks verified runtime tool availability",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="worker",
        name="AI Worker",
        node_type=NodeType.AGENT,
        role="Executor that runs ticks and delegates execution",
        owner="kernel.runtime",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="planner",
        name="Planner Agent",
        node_type=NodeType.AGENT,
        role="Turns goals into plans using Kernel knowledge",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="execution_engine",
        name="Execution Engine",
        node_type=NodeType.SERVICE,
        role="Executes approved structured plans",
        owner="kernel",
        status=NodeStatus.ACTIVE,
    ))
    model.add_node(SystemNode(
        id="github",
        name="GitHub",
        node_type=NodeType.RESOURCE,
        role="Source code repository and commit target",
        owner="external",
        status=NodeStatus.ACTIVE,
        capabilities=["github.read", "github.write"],
    ))
    model.add_node(SystemNode(
        id="google_drive",
        name="Google Drive",
        node_type=NodeType.RESOURCE,
        role="Knowledge storage and document source",
        owner="external",
        status=NodeStatus.ACTIVE,
        capabilities=["drive.read", "drive.create_doc", "drive.append_doc"],
    ))
    model.add_node(SystemNode(
        id="mcp",
        name="MCP Gateway",
        node_type=NodeType.SERVICE,
        role="Tool and integration gateway",
        owner="external",
        status=NodeStatus.ACTIVE,
        capabilities=["mcp.call"],
    ))

    model.add_relationship(SystemRelationship("kernel", "kernel.runtime", RelationshipType.OWNS, "Kernel owns runtime state."))
    model.add_relationship(SystemRelationship("kernel", "kernel.memory", RelationshipType.OWNS, "Kernel owns memory."))
    model.add_relationship(SystemRelationship("kernel", "kernel.governance", RelationshipType.OWNS, "Kernel owns governance."))
    model.add_relationship(SystemRelationship("kernel", "kernel.capability", RelationshipType.OWNS, "Kernel owns capability registry."))
    model.add_relationship(SystemRelationship("kernel", "kernel.tool_registry", RelationshipType.OWNS, "Kernel owns verified tool registry."))
    model.add_relationship(SystemRelationship("worker", "kernel.runtime", RelationshipType.USES, "Worker uses Kernel Runtime queue and ticks."))
    model.add_relationship(SystemRelationship("worker", "execution_engine", RelationshipType.EXECUTES, "Worker delegates execution work."))
    model.add_relationship(SystemRelationship("planner", "kernel.memory", RelationshipType.USES, "Planner uses memory for prior decisions."))
    model.add_relationship(SystemRelationship("planner", "kernel.governance", RelationshipType.USES, "Planner uses governance for decision constraints."))
    model.add_relationship(SystemRelationship("planner", "kernel.capability", RelationshipType.USES, "Planner checks designed capabilities."))
    model.add_relationship(SystemRelationship("execution_engine", "github", RelationshipType.WRITES, "Execution Engine writes code changes to GitHub."))
    model.add_relationship(SystemRelationship("kernel", "google_drive", RelationshipType.READS, "Kernel reads knowledge sources through Drive integrations."))
    model.add_relationship(SystemRelationship("kernel.tool_registry", "mcp", RelationshipType.USES, "Tool Registry verifies MCP tool availability."))

    return model


system_model = build_foundation_system_model()
