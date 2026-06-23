from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrungHuyenKernel:
    """Nhân điều hành tối giản của Trung Huyền OS."""

    def __init__(self) -> None:
        self.plugins: Dict[str, Dict[str, Any]] = {}
        self.events: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {}

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "kernel": "trung_huyen_os",
            "plugin_count": len(self.plugins),
            "event_count": len(self.events),
            "state_keys": sorted(self.state.keys()),
            "plugins": list(self.plugins.values()),
        }

    def register_plugin(self, name: str, capability: str, owner: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        plugin = {
            "name": name,
            "capability": capability,
            "owner": owner,
            "status": "registered",
            "registered_at": now(),
            "metadata": metadata or {},
        }
        self.plugins[name] = plugin
        self.publish("kernel.plugin.registered", "kernel", plugin)
        return {"status": "registered", "plugin": plugin}

    def publish(self, topic: str, source: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        event = {
            "topic": topic,
            "source": source,
            "payload": payload or {},
            "created_at": now(),
        }
        self.events.append(event)
        return {"status": "published", "event": event}

    def recent_events(self, limit: int = 50) -> Dict[str, Any]:
        return {"status": "ok", "events": self.events[-limit:]}

    def set_state(self, key: str, value: Any) -> Dict[str, Any]:
        self.state[key] = value
        self.publish("kernel.state.updated", "kernel", {"key": key, "value": value})
        return {"status": "ok", "key": key, "value": value}

    def get_state(self, key: str | None = None) -> Dict[str, Any]:
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
        ]
        registered = []
        for name, capability, owner in defaults:
            if name not in self.plugins:
                registered.append(self.register_plugin(name, capability, owner))
        self.set_state("kernel.bootstrapped", True)
        return {"status": "bootstrapped", "registered": registered, "kernel": self.status()}


kernel = TrungHuyenKernel()
