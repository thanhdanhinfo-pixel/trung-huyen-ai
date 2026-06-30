from fastapi import APIRouter 
from system import event_bus
from system.event_retention import event_retention

router=APIRouter(prefix='/system',tags=['system-events'])
@router.get('/events')
def events(limit:int=50): return event_bus.recent(limit)
@router.get('/events/stats')
def stats(): return event_bus.stats()
@router.get('/events/retention')
def retention(): return event_retention.policy()
