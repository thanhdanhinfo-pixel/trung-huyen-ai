from datetime import date
from pathlib import Path 
import yaml
from system.evolution.learning import learning_engine
from system.event_bus import event_bus
BASE=Path(__file__).parent.parent/'knowledge'
DECISIONS=BASE/'decisions.yaml'
class AdaptationEngine:
    def adapt(self):
        learned=learning_engine.learn()
        decision_data=yaml.safe_load(DECISIONS.read_text(encoding='utf-8')) or {'decisions':[]}
        new_decision={'id':f"D{len(decision_data['decisions'])+1:03d}",'decision':'apply_learned_patterns','patterns':learned.get('rule_candidates',[]),'date':str(date.today())}
        decision_data['decisions'].append(new_decision)
        DECISIONS.write_text(yaml.safe_dump(decision_data,allow_unicode=True,sort_keys=False),encoding='utf-8')
        event_bus.publish('ADAPTATION_APPLIED',{'decision_id':new_decision['id'],'patterns':new_decision['patterns']})
        return {'status':'adapted','decision':new_decision,'applied_patterns':learned.get('rule_candidates',[])}
adaptation_engine=AdaptationEngine()
