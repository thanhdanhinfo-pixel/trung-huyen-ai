from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Capability:
    """A single capability known by the AI Kernel."""

    name: str
    enabled: bool
    provider: str
    level: str = "unknown"
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "enabled": self.enabled,
            "provider": self.provider,
            "level": self.level,
            "description": self.description,
            "metadata": self.metadata,
        }


@dataclass
class CapabilityRegistry:
    """Capability layer of the AI Kernel.

    This answers the Kernel question:
    "What can I do?"

    The first version is declarative. Future versions will actively probe MCP,
    GitHub, Drive, Cloud Run and logs to verify capabilities at runtime.
    """

    capabilities: Dict[str, Capability] = field(default_factory=dict)

    @classmethod
    def load_default(cls) -> "CapabilityRegistry":
        registry = cls()
        registry.register("github.read", True, "github", "read", "Read repository files.")
        registry.register("github.write", True, "github", "write", "Create or update repository files.")
        registry.register("github.batch", True, "github", "write", "Execute multiple GitHub operations through Execution Engine.")
        registry.register("drive.read", True, "google_drive", "read", "Read Google Drive files and documents.")
        registry.register("drive.create_doc", True, "google_drive", "write", "Create Google Docs through MCP/Drive layer.")
        registry.register("drive.append_doc", True, "google_drive", "write", "Append content to Google Docs.")
        registry.register("mcp.call", True, "mcp", "execute", "Call MCP tools.")
        registry.register("execution.plan", True, "execution_engine", "execute", "Execute structured execution plans.")
        registry.register("worker.tick", True, "ai_worker", "execute", "Run one Worker heartbeat/tick.")
        registry.register("cloudrun.logs", False, "cloud_run", "read", "Read Cloud Run logs. Not yet verified.")
        registry.register("cloudrun.deploy", False, "cloud_run", "admin", "Deploy/restart Cloud Run. Not yet verified.")
        return registry

    def register(self, name: str, enabled: bool, provider: str, level: str = "unknown", description: str = "", metadata: Dict[str, Any] | None = None) -> Capability:
        capability = Capability(
            name=name,
            enabled=enabled,
            provider=provider,
            level=level,
            description=description,
            metadata=metadata or {},
        )
        self.capabilities[name] = capability
        return capability

    def can(self, name: str) -> bool:
        capability = self.capabilities.get(name)
        return bool(capability and capability.enabled)

    def get(self, name: str) -> Dict[str, Any] | None:
        capability = self.capabilities.get(name)
        return capability.as_dict() if capability else None

    def as_dict(self) -> Dict[str, Any]:
        return {
            name: capability.as_dict()
            for name, capability in self.capabilities.items()
        }

    def validate(self) -> Dict[str, Any]:
        disabled = [
            capability.as_dict()
            for capability in self.capabilities.values()
            if not capability.enabled
        ]
        return {
            "status": "ok",
            "capability_count": len(self.capabilities),
            "enabled_count": len(self.capabilities) - len(disabled),
            "disabled_count": len(disabled),
            "disabled": disabled,
        }

    def summary(self) -> Dict[str, List[str]]:
        enabled = []
        disabled = []
        for name, capability in self.capabilities.items():
            if capability.enabled:
                enabled.append(name)
            else:
                disabled.append(name)
        return {
            "enabled": enabled,
            "disabled": disabled,
        }


def load_capabilities() -> CapabilityRegistry:
    return CapabilityRegistry.load_default()


capabilities = load_capabilities()
