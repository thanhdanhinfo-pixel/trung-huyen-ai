from datetime import date
from pathlib import Path 
import yaml
from system import event_bus
BASE=Path(__file__).parent.parent/'knowledge'
class ReflectionEngine:
    def reflect_on_day(self):
        events=event_bus.recent(100)
        lessons=yaml.safe_load((BASE/'lessons.yaml').read_text(encoding='utf-8'))
        return {'date':str(date.today()),'event_count':len(events),'known_lessons':len(lessons.get('lessons',[])),'lessons':[x['title'] for x in lessons.get('lessons',[])]}
reflection_engine=ReflectionEngine()
