from system.reflection_engine import reflection_engine
from system.learning_engine import learning_engine
from system.adaptation_engine import adaptation_engine
from system.knowledge_graph import knowledge_graph
from system.event_bus import event_bus

class EvolutionEngine:
    def evolve(self):
        reflection = reflection_engine.reflect_on_day()
        learning = learning_engine.learn()
        adaptation = adaptation_engine.adapt()
        knowledge = knowledge_graph.snapshot()

        result = {
            'status': 'evolving',
            'reflection': reflection,
            'learning_patterns': learning.get('patterns', []),
            'adaptation': adaptation.get('decision', {}),
            'knowledge': knowledge,
        }

        event_bus.publish('EVOLUTION_CYCLE_COMPLETED', {
            'patterns': len(learning.get('patterns', [])),
            'decisions': knowledge.get('decision_count', 0)
        })

        return result


evolution_engine = EvolutionEngine()
