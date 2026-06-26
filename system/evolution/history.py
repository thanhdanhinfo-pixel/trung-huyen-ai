from datetime import datetime
class EvolutionHistory:
    def __init__(self):
        self.items=[]
    def record(self,event,data=None):
        self.items.append({'time':datetime.utcnow().isoformat()+'Z','event':event,'data':data or {}})
    def timeline(self,limit=50):
        return self.items[-limit:]
evolution_history=EvolutionHistory()
