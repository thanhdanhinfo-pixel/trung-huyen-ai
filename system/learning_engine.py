from system.reflection_engine import reflection_engine

class LearningEngine:
    def learn(self):
        reflection = reflection_engine.reflect_on_day()
        return {
            'status': 'learned',
            'patterns': reflection.get('lessons', []),
            'rule_candidates': [
                'always_refresh_context_before_patch'
            ]
        }

learning_engine = LearningEngine()
