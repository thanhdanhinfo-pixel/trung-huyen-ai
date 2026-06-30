from pathlib import Path
import json 
P=Path('system/knowledge/event_acks.json')
class EventAckStore:
    def append(self,ack):
        P.parent.mkdir(parents=True,exist_ok=True)
        data=[]
        if P.exists():
            data=json.loads(P.read_text(encoding='utf-8'))
        data.append(ack)
        P.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
        return {'persisted':True,'count':len(data)}
event_ack_store=EventAckStore()
