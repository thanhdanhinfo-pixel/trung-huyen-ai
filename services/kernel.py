from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class KernelPlugin:
    name: str
    capability: str
    owner: str
    status: str = "registered"
    registered_at: str = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KernelEvent:
    topic: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TrungHuyenKernel:
    """Nhân điều hành Trung Huyền OS.

    Kernel là trục điều phối duy nhất. Các service khác phải đăng ký như plugin
    thay vì hoạt động rời rạc.
    """

    def __init__(self) -> None:
        self.plugins: Dict[str, KernelPlugin] = {}
        self.events: List[KernelEvent] = []
        self.handlers: Dict[str, List[Callable[[KernelEvent], None]]] = {}
        self.state: Dict[str, Any] = {}

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "kernel": "trung_huyen_os",
            "plugin_count": len(self.plugins),
            "event_count": len(self.events),
            "state_keys": sorted(self.state.keys()),
            "plugins": [plugin.to_dict() for plugin in self.plugins.values()],
        }

    def register_plugin(
        self,
        name: str,
        capability: str,
        owner: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        plugin = KernelPlugin(
            name=name,
            capability=capability,
            owner=owner,
            metadata=metadata or {},
        )
        self.plugins[name] = plugin
        self.publish("kernel.plugin.registered", "kernel", plugin.to_dict())
        return {"status": "registered", "plugin": plugin.to_dict()}

    def unregister_plugin(self, name: str) -> Dict[str, Any]:
        plugin = self.plugins.pop(name, None)
        if not plugin:
            return {"status": "not_found", "plugin": name}
        self.publish("kernel.plugin.unregistered", "kernel", plugin.to_dict())
        return {"status": "unregistered", "plugin": plugin.to_dict()}

    def list_plugins(self, capability: Optional[str] = None) -> Dict[str, Any]:
        plugins = list(self.plugins.values())
        if capability:
            plugins = [plugin for plugin in plugins if plugin.capability == capability]
        return {"status": "ok", "plugins": [plugin.to_dict() for plugin in plugins]}

    def publish(self, topic: str, source: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event = KernelEvent(topic=topic, source=source, payload=payload or {})
        self.events.append(event)
        for handler in self.handlers.get(topic, []):
            handler(event)
        for handler in self.handlers.get("*", []):
            handler(event)
        return {"status": "published", "event": event.to_dict()}

    def recent_events(self, limit: int = 50) -> Dict[str, Any]:
        return {"status": "ok", "events": [event.to_dict() for event in self.events[-limit:]]}

    def set_state(self, key: str, value: Any, source: str = "kernel") -> Dict[str, Any]:
        self.state[key] = value
        self.publish("kernel.state.updated", source, {"key": key, "value": value})
        return {"status": "ok", "key": key, "value": value}

    def get_state(self, key: Optional[str] = None) -> Dict[str, Any]:
        if key:
            return {"status": "ok", "key": key, "value": self.state.get(key)}
        return {"status": "ok", "state": self.state}

    def bootstrap(self) -> Dict[str, Any]:
        defaults = [
            ("task_planner", "planning", "ai_ceo"),
            ("execution_queue", "execution", "runtime_director"),
            ("worker_pool", "execution", "runtime_director"),
            ("supervisor", "monitoring", "monitoring_director"),
            ("developer_runtime", "development", "runtime_director"),
            ("repository_manager", "repository", "cto"),
            ("repository_governor", "governance", "ciso"),
            ("repository_health", "monitoring", "monitoring_director"),
        ]
        results = []
        for name, capability, owner in defaults:
            if name not in self.plugins:
                results.append(self.register_plugin(name=name, capability=capability, owner=owner))
        self.set_state("kernel.bootstrapped", True)
        return {"status": "bootstrapped", "registered": results, "kernel": self.status()}


kernel = TrungHuyenKernel()
