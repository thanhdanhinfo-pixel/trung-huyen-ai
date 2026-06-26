from datetime import datetime

class EventAck:
    def __init__(self):
        self._acks = []

    def acknowledge(self, event_id: str, consumer: str):
        ack = {
            'event_id': event_id,
            'consumer': consumer,
            'acknowledged_at': datetime.utcnow().isoformat() + 'Z'
        }
        self._acks.append(ack)
        return ack

    def snapshot(self):
        return {'count': len(self._acks), 'acks': self._acks[-100:]}


event_ack = EventAck()
