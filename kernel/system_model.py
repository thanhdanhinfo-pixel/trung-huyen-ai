from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .relationship import RelationshipType, SystemRelationship
from .system_node import NodeStatus, NodeType, SystemNode


@dataclass
class SystemModel:
    """Digital Twin of TRUNG_HUYEN_AI_OS."""

    nodes: Dict[str, SystemNode] = field(default_factory=dict)
    relationships: List[SystemRelationship] = field(default_factory=list)

    def add_node(self, node: SystemNode) -> SystemNode:
        self.nodes[node.id] = node
        return node

    def add_relationship(self, relationship: SystemRelationship) -> SystemRelationship:
        key = (relationship.source, relationship.target, relationship.relation.value)
        for existing in self.relationships:
            existing_key = (existing.source, existing.target, existing.relation.value)
            if existing_key == key:
                return existing
        self.relationships.append(relationship)
        return relationship

    def get_node(self, node_id: str) -> Optional[SystemNode]:
        return self.nodes.get(node_id)

    def find_nodes_by_type(self, node_type: NodeType) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self.nodes.values() if node.node_type == node_type]

    def dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        targets = self._dependency_targets(node_id)
        return [self.nodes[target].to_dict() for target in targets if target in self.nodes]

    def dependents(self, node_id: str) -> List[Dict[str, Any]]:
        sources = self._dependent_sources(node_id)
        return [self.nodes[source].to_dict() for source in sources if source in self.nodes]

    def owned_by(self, owner: str) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in self.nodes.values() if node.owner == owner]

    def impact(self, node_id: str) -> Dict[str, Any]:
        node = self.nodes.get(node_id)
        direct_dependencies = self._dependency_targets(node_id)
        direct_dependents = self._dependent_sources(node_id)
        transitive_dependencies = self._walk_dependencies(node_id)
        transitive_dependents = self._walk_dependents(node_id)

        return {
            "node": node.to_dict() if node else None,
            "exists": node is not None,
            "direct_dependencies": [self.nodes[item].to_dict() for item in direct_dependencies if item in self.nodes],
            "direct_dependents": [self.nodes[item].to_dict() for item in direct_dependents if item in self.nodes],
            "transitive_dependencies": [self.nodes[item].to_dict() for item in transitive_dependencies if item in self.nodes],
            "transitive_dependents": [self.nodes[item].to_dict() for item in transitive_dependents if item in self.nodes],
            "impact_radius": len(transitive_dependents),
            "dependency_depth": self.dependency_depth(node_id),
            "risk_level": self._impact_risk_level(len(transitive_dependents)),
            "criticality": self.criticality_score(node_id),
        }

    def relationships_for(self, node_id: str) -> List[Dict[str, Any]]:
        return [rel.to_dict() for rel in self.relationships if rel.source == node_id or rel.target == node_id]

    def summary(self) -> Dict[str, Any]:
        by_type: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        for node in self.nodes.values():
            by_type[node.node_type.value] = by_type.get(node.node_type.value, 0) + 1
            by_status[node.status.value] = by_status.get(node.status.value, 0) + 1
        return {"node_count": len(self.nodes), "relationship_count": len(self.relationships), "by_type": by_type, "by_status": by_status}

    def export(self) -> Dict[str, Any]:
        return {"summary": self.summary(), "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()}, "relationships": [relationship.to_dict() for relationship in self.relationships]}

    def detect_cycles(self) -> List[List[str]]:
        graph = {node_id: self._dependency_targets(node_id) for node_id in self.nodes}
        cycles: List[List[str]] = []
        visiting: List[str] = []
        visited: set[str] = set()
        cycle_keys: set[tuple[str, ...]] = set()

        def normalize_cycle(cycle: List[str]) -> tuple[str, ...]:
            body = cycle[:-1]
            if not body:
                return tuple(cycle)
            rotations = [tuple(body[i:] + body[:i]) for i in range(len(body))]
            best = min(rotations)
            return best + (best[0],)

        def dfs(node: str) -> None:
            if node in visiting:
                idx = visiting.index(node)
                cycle = visiting[idx:] + [node]
                key = normalize_cycle(cycle)
                if key not in cycle_keys:
                    cycle_keys.add(key)
                    cycles.append(cycle)
                return
            if node in visited:
                return
            visiting.append(node)
            for nxt in graph.get(node, []):
                if nxt in self.nodes:
                    dfs(nxt)
            visiting.pop()
            visited.add(node)

        for node_id in graph:
            dfs(node_id)
        return cycles

    def dependency_depth(self, node_id: str) -> int:
        def dfs(current: str, seen: set[str]) -> int:
            deps = self._dependency_targets(current)
            if not deps:
                return 0
            depth = 0
            for dep in deps:
                if dep in seen or dep not in self.nodes:
                    continue
                depth = max(depth, 1 + dfs(dep, seen | {dep}))
            return depth
        return dfs(node_id, {node_id})

    def criticality_score(self, node_id: str) -> Dict[str, Any]:
        direct_dependents = self._dependent_sources(node_id)
        transitive_dependents = self._walk_dependents(node_id)
        dependencies = self._dependency_targets(node_id)
        depth = self.dependency_depth(node_id)
        score = (len(direct_dependents) * 3) + len(transitive_dependents) + len(dependencies) + depth
        if score > 20:
            level = "critical"
        elif score > 10:
            level = "high"
        elif score > 3:
            level = "medium"
        else:
            level = "low"
        return {"node_id": node_id, "score": score, "level": level, "direct_dependents": len(direct_dependents), "transitive_dependents": len(transitive_dependents), "dependencies": len(dependencies), "dependency_depth": depth, "is_architecture_risk": False}

    def risk_nodes(self) -> List[Dict[str, Any]]:
        risks: List[Dict[str, Any]] = []
        for cycle in self.detect_cycles():
            risks.append({"type": "cycle", "level": "critical", "score": 50, "cycle": cycle})
        for node_id in self._orphan_nodes():
            risks.append({"type": "orphan", "level": "warning", "score": 5, "node_id": node_id})
        return risks

    def mermaid_graph(self) -> str:
        lines = ["graph TD"]
        for rel in self.relationships:
            if rel.relation in {RelationshipType.USES, RelationshipType.DEPENDS_ON, RelationshipType.OWNS}:
                source = self._mermaid_id(rel.source)
                target = self._mermaid_id(rel.target)
                label = rel.relation.value
                lines.append(f"    {source}[\"{rel.source}\"] -- {label} --> {target}[\"{rel.target}\"]")
        return "\n".join(lines)

    def architecture_report(self) -> Dict[str, Any]:
        cycles = self.detect_cycles()
        critical_nodes = sorted([self.criticality_score(node_id) for node_id in self.nodes], key=lambda item: item["score"], reverse=True)
        orphans = self._orphan_nodes()
        risks = self.risk_nodes()
        risk_score = sum(item.get("score", 0) for item in risks)
        health = "good" if risk_score < 20 else "warning" if risk_score < 80 else "critical"
        high_criticality = [item for item in critical_nodes if item["level"] in {"critical", "high"}]

        return {
            "summary": self.summary(),
            "health": health,
            "risk_score": risk_score,
            "cycles": cycles,
            "cycle_count": len(cycles),
            "orphans": orphans,
            "orphan_count": len(orphans),
            "risk_nodes": risks,
            "risk_node_count": len(risks),
            "critical_nodes": critical_nodes[:10],
            "high_criticality_count": len(high_criticality),
            "high_risk_count": len(risks),
            "mermaid": self.mermaid_graph(),
        }

    def _orphan_nodes(self) -> List[str]:
        connected_nodes = set()
        for rel in self.relationships:
            connected_nodes.add(rel.source)
            connected_nodes.add(rel.target)
        return [node_id for node_id in self.nodes if node_id not in connected_nodes]

    def _dependency_targets(self, node_id: str) -> List[str]:
        return sorted({rel.target for rel in self.relationships if rel.source == node_id and rel.relation in {RelationshipType.DEPENDS_ON, RelationshipType.USES}})

    def _dependent_sources(self, node_id: str) -> List[str]:
        return sorted({rel.source for rel in self.relationships if rel.target == node_id and rel.relation in {RelationshipType.DEPENDS_ON, RelationshipType.USES}})

    def _walk_dependencies(self, node_id: str) -> List[str]:
        return self._walk_graph(start=node_id, next_nodes=self._dependency_targets)

    def _walk_dependents(self, node_id: str) -> List[str]:
        return self._walk_graph(start=node_id, next_nodes=self._dependent_sources)

    def _walk_graph(self, start: str, next_nodes: Any) -> List[str]:
        visited: set[str] = set()
        ordered: List[str] = []
        queue: List[str] = list(next_nodes(start))
        while queue:
            current = queue.pop(0)
            if current == start or current in visited:
                continue
            visited.add(current)
            ordered.append(current)
            queue.extend(next_nodes(current))
        return ordered

    def _impact_risk_level(self, impact_radius: int) -> str:
        if impact_radius >= 10:
            return "high"
        if impact_radius >= 4:
            return "medium"
        if impact_radius >= 1:
            return "low"
        return "none"

    def _mermaid_id(self, node_id: str) -> str:
        return node_id.replace(".", "_").replace("-", "_").replace("/", "_")


def build_foundation_system_model() -> SystemModel:
    """Build the first Kernel-first Digital Twin foundation."""
    model = SystemModel()

    model.add_node(SystemNode(id="kernel", name="AI Kernel", node_type=NodeType.KERNEL, role="Central system intelligence and coordination layer", owner="TRUNG_HUYEN_AI_OS", status=NodeStatus.ACTIVE, lifecycle="v2_foundation"))
    model.add_node(SystemNode(id="kernel.runtime", name="Kernel Runtime", node_type=NodeType.KERNEL_COMPONENT, role="Owns runtime state, ticks and task queue", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="kernel.memory", name="Kernel Memory", node_type=NodeType.KERNEL_COMPONENT, role="Stores decisions, lessons and architecture knowledge", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="kernel.governance", name="Kernel Governance", node_type=NodeType.KERNEL_COMPONENT, role="Validates decisions and actions against principles", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="kernel.capability", name="Kernel Capability", node_type=NodeType.KERNEL_COMPONENT, role="Describes designed system capabilities", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="kernel.tool_registry", name="Kernel Tool Registry", node_type=NodeType.KERNEL_COMPONENT, role="Tracks verified runtime tool availability", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="worker", name="AI Worker", node_type=NodeType.AGENT, role="Executor that runs ticks and delegates execution", owner="kernel.runtime", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="planner", name="Planner Agent", node_type=NodeType.AGENT, role="Turns goals into plans using Kernel knowledge", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="execution_engine", name="Execution Engine", node_type=NodeType.SERVICE, role="Executes approved structured plans", owner="kernel", status=NodeStatus.ACTIVE))
    model.add_node(SystemNode(id="github", name="GitHub", node_type=NodeType.RESOURCE, role="Source code repository and commit target", owner="external", status=NodeStatus.ACTIVE, capabilities=["github.read", "github.write"]))
    model.add_node(SystemNode(id="google_drive", name="Google Drive", node_type=NodeType.RESOURCE, role="Knowledge storage and document source", owner="external", status=NodeStatus.ACTIVE, capabilities=["drive.read", "drive.create_doc", "drive.append_doc"]))
    model.add_node(SystemNode(id="mcp", name="MCP Gateway", node_type=NodeType.SERVICE, role="Tool and integration gateway", owner="external", status=NodeStatus.ACTIVE, capabilities=["mcp.call"]))

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
