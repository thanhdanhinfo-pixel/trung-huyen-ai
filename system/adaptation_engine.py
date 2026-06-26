from system.learning_engine import learning_engine

class AdaptationEngine:
    def adapt(self):
        learned = learning_engine.learn()
        return {
            'status': 'adapted',
            'applied_patterns': learned.get('rule_candidates', [])
        }

adaptation_engine = AdaptationEngine()
