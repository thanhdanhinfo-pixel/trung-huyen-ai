from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryRecord:
    """A persistent memory item known by the AI Kernel."""

    type: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class KernelMemory:
    """Memory layer of the AI Kernel.

    This answers the Kernel question:
    "What have I learned or decided about this system?"

    Runtime is for current state. Memory is for accumulated decisions,
    principles, lessons and architecture notes.
    """

    records: List[MemoryRecord] = field(default_factory=list)

    def remember(
        self,
        type: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryRecord:
        if not title:
            raise ValueError("memory.title is required")
        if not content:
            raise ValueError("memory.content is required")

        record = MemoryRecord(
            type=type or "note",
            title=title,
            content=content,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.records.append(record)
        return record

    def decision(self, title: str, content: str, tags: Optional[List[str]] = None) -> MemoryRecord:
        return self.remember(
            type="decision",
            title=title,
            content=content,
            tags=tags or ["decision"],
        )

    def lesson(self, title: str, content: str, tags: Optional[List[str]] = None) -> MemoryRecord:
        return self.remember(
            type="lesson",
            title=title,
            content=content,
            tags=tags or ["lesson"],
        )

    def architecture_note(self, title: str, content: str, tags: Optional[List[str]] = None) -> MemoryRecord:
        return self.remember(
            type="architecture_note",
            title=title,
            content=content,
            tags=tags or ["architecture"],
        )

    def search(self, query: str = "", type: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        query_normalized = (query or "").lower().strip()
        results: List[MemoryRecord] = []

        for record in self.records:
            if type and record.type != type:
                continue
            if tag and tag not in record.tags:
                continue
            if query_normalized:
                haystack = f"{record.title}\n{record.content}".lower()
                if query_normalized not in haystack:
                    continue
            results.append(record)

        return [record.as_dict() for record in results]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "record_count": len(self.records),
            "records": [record.as_dict() for record in self.records],
        }

    def seed_foundation_memory(self) -> None:
        """Seed key architecture decisions for the refactor phase."""
        if self.records:
            return

        self.decision(
            title="AI OS refactor strategy",
            content=(
                "Build AI OS V2 in parallel with the legacy system. Do not break "
                "legacy modules during refactor. Migrate to Kernel only after the "
                "new Kernel is stable, then clean up legacy code."
            ),
            tags=["decision", "refactor", "kernel"],
        )
        self.architecture_note(
            title="Kernel-first architecture",
            content=(
                "AI Kernel is the single coordination layer for Identity, Registry, "
                "Runtime, Capability, Memory, Governance and Health. Other modules "
                "should gradually migrate to ask Kernel instead of owning system state."
            ),
            tags=["architecture", "kernel"],
        )


def load_memory() -> KernelMemory:
    memory = KernelMemory()
    memory.seed_foundation_memory()
    return memory


memory = load_memory()
