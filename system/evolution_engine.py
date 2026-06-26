from system.reflection_engine import reflection_engine
from system.learning_engine import learning_engine
from system.adaptation_engine import adaptation_engine
from system.knowledge_graph import knowledge_graph
from system.event_bus import event_bus

class EvolutionEngine:
    def evaluate(self):
        knowledge = knowledge_graph.snapshot()
        return {
            'status': 'evaluated',
            'decision_count': knowledge.get('decision_count', 0),
            'pattern_count': knowledge.get('pattern_count', 0),
            'recommendation': 'promote_stable_patterns' if knowledge.get('pattern_count', 0) > 0 else 'observe_more'
        }

    def evolve(self):
        r = reflection_engine.reflect_on_day()
        l = learning_engine.learn()
        a = adaptation_engine.adapt()
        k = knowledge_graph.snapshot()
        e = self.evaluate()
        promoted = l.get('rule_candidates', []) if e['recommendation'] == 'promote_stable_patterns' else []
        event_bus.publish('EVOLUTION_CYCLE_COMPLETED', {'promoted': promoted, 'evaluation': e})
        return {'status': 'evolving', 'evaluation': e, 'promoted_rules': promoted, 'knowledge': k, 'adaptation': a}

evolution_engine = EvolutionEngine()
