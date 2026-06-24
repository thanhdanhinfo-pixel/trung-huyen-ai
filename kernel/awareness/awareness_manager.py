from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from .capability_observer import capability_observer
from .configuration_observer import configuration_observer
from ..self_state import self_state
from ..runtime_observer import runtime_observer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AwarenessSnapshot:
    """Unified Kernel awareness snapshot."""

    observed_at: str = field(default_factory=utc_now)
    runtime: Dict[str, Any] = field(default_factory=dict)
    capability: Dict[str, Any] = field(default_factory=dict)
    system_model: Dict[str, Any] = field(default_factory=dict)
    discovery: Dict[str, Any] = field(default_factory=dict)
    repository_adapter: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    self_state: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observed_at": self.observed_at,
            "runtime": self.runtime,
            "capability": self.capability,
            "configuration": self.configuration,
            "self_state": self.self_state,
            "system_model": self.system_model,
            "discovery": self.discovery,
            "repository_adapter": self.repository_adapter,
        }


@dataclass
class AwarenessManager:
    """Central manager for AI Kernel awareness.

    AIKernel should remain the orchestration root, not a God Object.
    AwarenessManager owns the aggregation of observers and produces a unified
    self-awareness view for Planner, Worker, Health and future agents.
    """

    runtime: Any = field(default_factory=lambda: runtime_observer)
    capability: Any = field(default_factory=lambda: capability_observer)
    configuration: Any = field(default_factory=lambda: configuration_observer)
    self_state: Any = field(default_factory=lambda: self_state)
    last_snapshot: AwarenessSnapshot | None = None

    def observe(self, kernel: Any) -> AwarenessSnapshot:
        snapshot = AwarenessSnapshot(
            runtime=self.runtime.observe(kernel).to_dict(),
            capability=self.capability.observe(kernel).to_dict(),
            configuration=self.configuration.observe().to_dict(),
            self_state=self.self_state.to_dict(),
            system_model=kernel.system_model.summary(),
            discovery=kernel.discovery_status(),
            repository_adapter=kernel.repository_adapter.status(),
        )
        self.last_snapshot = snapshot
        return snapshot

    def summary(self, kernel: Any) -> Dict[str, Any]:
        return self.observe(kernel).to_dict()

    def status(self) -> Dict[str, Any]:
        if not self.last_snapshot:
            return {"status": "idle"}
        return {
            "status": "ok",
            "last_snapshot": self.last_snapshot.to_dict(),
        }


def load_awareness_manager() -> AwarenessManager:
    return AwarenessManager()


awareness_manager = load_awareness_manager()
