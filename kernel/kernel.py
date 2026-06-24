from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from .capability import load_capabilities
from .discovery import discovery_engine
from .governance import load_governance
from .health import load_health
from .memory import load_memory
from .registry import load_registry
from .runtime import runtime as kernel_runtime
from .system_model import system_model


@dataclass
class AIKernelIdentity:
    system_name: str = "TRUNG_HUYEN_AI_OS"
    role: str = "AI Chief Architect / AI CTO"
    mission: str = "Understand, operate and evolve the AI OS"
    owner: str = "Trung Huyen"
    architecture_version: str = "AI_OS_V2_KERNEL"

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AIKernel:
    identity: AIKernelIdentity = field(default_factory=AIKernelIdentity)
    registry: Any = field(default_factory=load_registry)
    runtime: Any = field(default_factory=lambda: kernel_runtime)
    capabilities: Any = field(default_factory=load_capabilities)
    memory: Any = field(default_factory=load_memory)
    governance: Any = field(default_factory=load_governance)
    health: Any = field(default_factory=load_health)
    system_model: Any = field(default_factory=lambda: system_model)
    discovery: Any = field(default_factory=lambda: discovery_engine)
    booted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def boot_status(self) -> Dict[str, Any]:
        health_report = self.health.check(self)
        return {
            "status": "ok" if health_report.get("status") == "ok" else "warning",
            "booted_at": self.booted_at,
            "identity": self.identity.as_dict(),
            "registry": self.registry.validate(),
            "runtime": self.runtime.snapshot(),
            "capabilities": self.capabilities.validate(),
            "memory": self.memory.as_dict(),
            "governance": self.governance.as_dict(),
            "health": health_report,
            "system_model": self.system_model.summary(),
            "discovery": self.discovery_status(),
        }

    def self_awareness(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.as_dict(),
            "registry": self.registry.as_dict(),
            "runtime": self.runtime.snapshot(),
            "capabilities": self.capabilities.summary(),
            "memory_records": self.memory.as_dict()["record_count"],
            "governance": self.governance.as_dict(),
            "health": self.health.check(self),
            "system_model": self.system_model.summary(),
        }

    def can(self, capability: str) -> bool:
        return self.capabilities.can(capability)

    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        return self.governance.validate_action(action)

    def find_node(self, node_id: str) -> Dict[str, Any] | None:
        node = self.system_model.get_node(node_id)
        return node.to_dict() if node else None

    def dependencies(self, node_id: str) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "dependencies": self.system_model.dependencies(node_id),
        }

    def dependents(self, node_id: str) -> Dict[str, Any]:
        return {
            "node_id": node_id,
            "dependents": self.system_model.dependents(node_id),
        }

    def impact(self, node_id: str) -> Dict[str, Any]:
        return self.system_model.impact(node_id)

    def system_summary(self) -> Dict[str, Any]:
        return self.system_model.summary()

    def export_system_model(self) -> Dict[str, Any]:
        return self.system_model.export()

    def discover(self, paths: list[str]) -> Dict[str, Any]:
        result = self.discovery.discover_from_paths(paths)
        return self.discovery.apply_to_model(self.system_model, result)

    def discovery_status(self) -> Dict[str, Any]:
        if not self.discovery.last_result:
            return {"status": "idle"}
        return self.discovery.last_result.to_dict()


kernel = AIKernel()
