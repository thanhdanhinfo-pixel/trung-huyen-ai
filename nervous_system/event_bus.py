from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Event:
    topic: str
    source: str
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EventBus:
    """Trung tâm sự kiện của Hệ Thần Kinh Trung Huyền OS."""

    def __init__(self) -> None:
        self.events: List[Event] = []
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def publish(self, topic: str, source: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        event = Event(topic=topic, source=source, payload=payload or {})
        self.events.append(event)
        for handler in self.subscribers.get(topic, []):
            handler(event)
        for handler in self.subscribers.get("*", []):
            handler(event)
        return {"status": "published", "event": event.to_dict()}

    def subscribe(self, topic: str, handler: Callable[[Event], None]) -> Dict[str, Any]:
        self.subscribers.setdefault(topic, []).append(handler)
        return {"status": "subscribed", "topic": topic, "subscriber_count": len(self.subscribers[topic])}

    def recent(self, limit: int = 50) -> Dict[str, Any]:
        return {"status": "ok", "events": [e.to_dict() for e in self.events[-limit:]]}

    def status(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "component": "he_than_kinh.event_bus",
            "event_count": len(self.events),
            "topics": sorted(self.subscribers.keys()),
        }


event_bus = EventBus()
