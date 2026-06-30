from pathlib import Path 
import json
from system.event_bus import event_bus
STORE=Path('system/knowledge/event_history.json')
def replay(limit=100):
    events=event_bus.recent(limit)
    STORE.parent.mkdir(parents=True,exist_ok=True)
    STORE.write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'mode':'replay','persisted':True,'events':events}
def sse_snapshot(limit=20):
    return {'mode':'sse-foundation','events':event_bus.recent(limit)}
