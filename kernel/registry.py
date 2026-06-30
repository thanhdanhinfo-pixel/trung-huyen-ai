from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from config import DRIVE_FOLDER_ID


@dataclass
class RegistryResource:
    """A resource known by the AI Kernel."""

    name: str
    type: str
    id: str
    role: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "id": self.id,
            "role": self.role,
            "metadata": self.metadata,
        }


@dataclass
class SystemRegistry:
    """Registry layer of the AI Kernel.

    This answers the second Kernel question:
    "What does my system contain, and where is it?"

    Environment variables are treated as bootstrap inputs only. The long-term
    target is a persistent registry document controlled by the Kernel.
    """

    knowledge_sources: List[RegistryResource] = field(default_factory=list)
    master_document: Optional[RegistryResource] = None
    fallback_drive_root: Optional[RegistryResource] = None

    @classmethod
    def load(cls) -> "SystemRegistry":
        knowledge_sources: List[RegistryResource] = []

        if DRIVE_FOLDER_ID:
            knowledge_sources.append(
                RegistryResource(
                    name="founder_drive_root",
                    type="drive",
                    id=DRIVE_FOLDER_ID,
                    role="knowledge_source",
                    metadata={"source": "DRIVE_FOLDER_ID"},
                )
            )

        master_resource = None

        fallback = None
        if DRIVE_FOLDER_ID:
            fallback = RegistryResource(
                name="default_drive_root",
                type="drive",
                id=DRIVE_FOLDER_ID,
                role="fallback_drive_root",
                metadata={"source": "DRIVE_FOLDER_ID", "note": "legacy fallback only"},
            )

        return cls(
            knowledge_sources=knowledge_sources,
            master_document=master_resource,
            fallback_drive_root=fallback,
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "knowledge_sources": [item.as_dict() for item in self.knowledge_sources],
            "master_document": self.master_document.as_dict() if self.master_document else None,
            "fallback_drive_root": self.fallback_drive_root.as_dict() if self.fallback_drive_root else None,
        }

    def validate(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []

        if not self.knowledge_sources:
            issues.append({
                "level": "warning",
                "code": "NO_KNOWLEDGE_SOURCES",
                "message": "No drive knowledge sources configured via KNOWLEDGE_SOURCES.",
            })

        if not self.master_document:
            issues.append({
                "level": "warning",
                "code": "NO_MASTER_DOCUMENT",
                "message": "No master document configured.",
            })

        if self.fallback_drive_root and not self.knowledge_sources:
            issues.append({
                "level": "info",
                "code": "USING_LEGACY_DRIVE_FOLDER_ID",
                "message": "System can still use DRIVE_FOLDER_ID as legacy fallback.",
            })

        return {
            "status": "ok" if not issues else "warning",
            "knowledge_source_count": len(self.knowledge_sources),
            "has_master_document": self.master_document is not None,
            "has_fallback_drive_root": self.fallback_drive_root is not None,
            "issues": issues,
        }

    def get_resource(self, name: str) -> Optional[RegistryResource]:
        for resource in self.knowledge_sources:
            if resource.name == name:
                return resource
        if self.master_document and self.master_document.name == name:
            return self.master_document
        if self.fallback_drive_root and self.fallback_drive_root.name == name:
            return self.fallback_drive_root
        return None


def load_registry() -> SystemRegistry:
    return SystemRegistry.load()
