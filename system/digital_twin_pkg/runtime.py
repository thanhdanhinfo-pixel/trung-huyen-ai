from __future__ import annotations  
from datetime import date
from pathlib import Path
from typing import Any, Dict, List
import yaml
class DigitalTwin:
    BASE=Path(__file__).parent.parent
    FILE_NAME='DIGITAL_TWIN.yaml'
    def __init__(self,path:str|None=None): self.path=Path(path) if path else self.BASE/self.FILE_NAME
    def load(self)->Dict[str,Any]:
        with open(self.path,'r',encoding='utf-8') as f: return yaml.safe_load(f) or {}
    def save(self,data:Dict[str,Any])->None:
        with open(self.path,'w',encoding='utf-8') as f: yaml.safe_dump(data,f,allow_unicode=True,sort_keys=False)
    def snapshot(self)->Dict[str,Any]:
        d=self.load(); return {'system_name':d.get('system_name'),'status':d.get('status'),'identity':d.get('identity',{}),'runtime':d.get('runtime',{}),'health':d.get('health',{}),'next_required_steps':self.predict_next_steps()}
    def health(self): return self.load().get('health',{})
    def update_health(self,component,state):
        d=self.load(); h=d.setdefault('health',{}); h[component]=state; d['last_updated']=str(date.today()); self.save(d); return h
    def append_evolution(self,event,event_date=None):
        d=self.load(); hist=d.setdefault('evolution_history',[]); hist.append({'date':event_date or str(date.today()),'event':event}); d['last_updated']=str(date.today()); self.save(d); return hist
    def predict_next_steps(self)->List[str]: return self.load().get('predictions',{}).get('next_required_steps',[])
digital_twin=DigitalTwin()
