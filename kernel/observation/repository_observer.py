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

        high_coupling_nodes = []
        orphan_candidates = []

        for node_id, node in nodes.items():
            dependencies = node.get("dependencies", []) or []
            if len(dependencies) >= 8:
                high_coupling_nodes.append({
                    "node_id": node_id,
                    "dependency_count": len(dependencies),
                })
            if not dependencies:
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

        return ObservationResult(
            source=self.source,
            status="ok" if not warnings else "warning",
            metrics=metrics,
            warnings=warnings,
        )


repository_observer = RepositoryObserver()
