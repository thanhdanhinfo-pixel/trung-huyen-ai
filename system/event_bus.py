from collections import deque
from datetime import datetime
from typing import Any, Dict, List

class EventBus:
    def __init__(self, max_events: int = 200):
        self._events = deque(maxlen=max_events)

    def publish(self, event_type: str, payload: Dict[str, Any] | None = None):
        event = {
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'payload': payload or {}
        }
        self._events.append(event)
        return event

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self._events)[-limit:]

    def stats(self):
        return {'count': len(self._events)}


event_bus = EventBus()
event_bus.publish('EVENT_BUS_INITIALIZED')
