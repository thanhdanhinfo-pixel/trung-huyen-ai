from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RelationshipType(str, Enum):
    USES = "uses"
    OWNS = "owns"
    DEPENDS_ON = "depends_on"
    PROVIDES = "provides"
    EXECUTES = "executes"
    READS = "reads"
    WRITES = "writes"
    DISCOVERS = "discovers"


@dataclass
class SystemRelationship:
    source: str
    target: str
    relation: RelationshipType
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation.value,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }
