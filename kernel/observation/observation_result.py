from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from ..relationship import SystemRelationship
from ..system_node import SystemNode


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ObservationResult:
    """Provider-neutral observation result.

    Observers collect facts from real sources and normalize them into nodes,
    relationships, metrics and warnings for the Kernel Digital Twin.
    """

    source: str
    status: str = "ok"
    observed_at: str = field(default_factory=utc_now)
    nodes: List[SystemNode] = field(default_factory=list)
    relationships: List[SystemRelationship] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "status": self.status,
            "observed_at": self.observed_at,
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "nodes": [node.to_dict() for node in self.nodes],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "metrics": self.metrics,
            "warnings": self.warnings,
        }
