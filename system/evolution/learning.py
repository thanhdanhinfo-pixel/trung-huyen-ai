from pathlib import Path
import yaml
from system.evolution.reflection import reflection_engine
BASE=Path(__file__).parent.parent/'knowledge'
class LearningEngine:
    def learn(self):
        reflection=reflection_engine.reflect_on_day()
        patterns=yaml.safe_load((BASE/'patterns.yaml').read_text(encoding='utf-8'))
        return {'status':'learned','patterns':[p['name'] for p in patterns.get('patterns',[])],'rule_candidates':[p['name'] for p in patterns.get('patterns',[])],'reflection':reflection}
learning_engine=LearningEngine()
