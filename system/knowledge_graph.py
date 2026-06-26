from pathlib import Path
import yaml

BASE = Path(__file__).parent / 'knowledge'

class KnowledgeGraph:
    def _load(self, name):
        p = BASE / name
        return yaml.safe_load(p.read_text(encoding='utf-8')) or {}

    def snapshot(self):
        lessons = self._load('lessons.yaml').get('lessons', [])
        patterns = self._load('patterns.yaml').get('patterns', [])
        decisions = self._load('decisions.yaml').get('decisions', [])

        return {
            'lesson_count': len(lessons),
            'pattern_count': len(patterns),
            'decision_count': len(decisions),
            'links': [
                {'lesson': l.get('id'), 'pattern': p.get('id')}
                for l, p in zip(lessons, patterns)
            ]
        }

knowledge_graph = KnowledgeGraph()
