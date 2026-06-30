from pathlib import Path
from typing import Any, Dict 
try:
    import yaml
except Exception:
    yaml=None
class SystemAwareness:
    BASE=Path(__file__).parent.parent
    def _load_yaml(self,name:str)->Dict[str,Any]:
        if yaml is None:
            return {'error':'PyYAML not installed','file':name}
        p=self.BASE/name
        with open(p,'r',encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    def self_state(self): return self._load_yaml('SELF_STATE.yaml')
    def capability_registry(self): return self._load_yaml('CAPABILITY_REGISTRY.yaml')
    def system_model(self): return self._load_yaml('SYSTEM_MODEL.yaml')
    def digital_twin(self): return self._load_yaml('DIGITAL_TWIN.yaml')
    def snapshot(self):
        s=self.self_state(); c=self.capability_registry(); d=self.digital_twin()
        return {'system_name':s.get('system_name'),'operating_mode':s.get('operating_mode'),'evolution_stage':s.get('evolution_stage'),'capability_groups':len(c.get('capability_groups',{})),'digital_twin_status':d.get('status')}
    def next_priorities(self):
        return self.digital_twin().get('predictions',{}).get('next_required_steps',[])
system_awareness=SystemAwareness()
