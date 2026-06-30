from datetime import datetime 
from system.events.ack_store import event_ack_store

class EventAck:
    def __init__(self):
        self._acks=[]

    def acknowledge(self,event_id:str,consumer:str):
        ack={
            'event_id':event_id,
            'consumer':consumer,
            'acknowledged_at':datetime.utcnow().isoformat()+'Z'
        }
        self._acks.append(ack)
        event_ack_store.append(ack)
        return ack

    def snapshot(self):
        return {'count':len(self._acks),'acks':self._acks[-100:]}

event_ack=EventAck()
