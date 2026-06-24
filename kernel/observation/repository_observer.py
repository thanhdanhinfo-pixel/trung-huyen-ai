from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .observation_result import ObservationResult


@dataclass
class RepositoryObserver:
    """Observe repository-derived Digital Twin state.

    V1 reads from the Kernel SystemModel, which is already populated by the
    repository scanner and discovery engine. Later versions can read GitHub
    directly and compare repository reality with the Digital Twin.
    """

    source: str = "repository"

    def observe(self, kernel: Any) -> ObservationResult:
        model = kernel.export_system_model()
        summary: Dict[str, Any] = model.get("summary", {})
        nodes: Dict[str, Any] = model.get("nodes", {})
        relationships = model.get("relationships", [])

        by_type = summary.get("by_type", {}) or {}
        by_status = summary.get("by_status", {}) or {}

        connected_nodes = set()
        incoming_count: Dict[str, int] = {node_id: 0 for node_id in nodes}
        outgoing_count: Dict[str, int] = {node_id: 0 for node_id in nodes}

        for rel in relationships:
            source = rel.get("source")
            target = rel.get("target")
            if source:
                connected_nodes.add(source)
                outgoing_count[source] = outgoing_count.get(source, 0) + 1
            if target:
                connected_nodes.add(target)
                incoming_count[target] = incoming_count.get(target, 0) + 1

        high_coupling_nodes = []
        orphan_candidates = []
        isolated_nodes = []

        for node_id, node in nodes.items():
            dependencies = node.get("dependencies", []) or []
            total_outgoing = outgoing_count.get(node_id, 0)
            total_incoming = incoming_count.get(node_id, 0)

            if len(dependencies) >= 8 or total_outgoing >= 8:
                high_coupling_nodes.append({
                    "node_id": node_id,
                    "dependency_count": len(dependencies),
                    "outgoing_relationship_count": total_outgoing,
                })

            if node_id not in connected_nodes:
                isolated_nodes.append(node_id)
                orphan_candidates.append(node_id)

        metrics = {
            "node_count": summary.get("node_count", len(nodes)),
            "relationship_count": summary.get("relationship_count", len(relationships)),
            "service_count": by_type.get("service", 0),
            "kernel_component_count": by_type.get("kernel_component", 0),
            "agent_count": by_type.get("agent", 0),
            "resource_count": by_type.get("resource", 0),
            "active_count": by_status.get("active", 0),
            "discovered_count": by_status.get("discovered", 0),
            "connected_node_count": len(connected_nodes),
            "isolated_node_count": len(isolated_nodes),
            "high_coupling_count": len(high_coupling_nodes),
            "orphan_candidate_count": len(orphan_candidates),
        }

        warnings = []
        if high_coupling_nodes:
            warnings.append({
                "code": "HIGH_COUPLING_NODES",
                "count": len(high_coupling_nodes),
                "nodes": high_coupling_nodes[:10],
            })
        if isolated_nodes:
            warnings.append({
                "code": "ISOLATED_NODES",
                "count": len(isolated_nodes),
                "nodes": isolated_nodes[:20],
            })

        return ObservationResult(
            source=self.source,
            status="ok" if not warnings else "warning",
            metrics=metrics,
            warnings=warnings,
        )


repository_observer = RepositoryObserver()
