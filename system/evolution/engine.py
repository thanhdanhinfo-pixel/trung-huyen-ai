from system.evolution.reflection import reflection_engine 
from system.evolution.learning import learning_engine
from system.evolution.adaptation import adaptation_engine
from system.knowledge_graph import knowledge_graph
from system.event_bus import event_bus
from system.evolution.history import evolution_history
class EvolutionEngine:
    def evaluate(self):
        k=knowledge_graph.snapshot()
        return {'status':'evaluated','score':k.get('pattern_count',0)+k.get('decision_count',0)}
    def archive_candidates(self):
        return {'archived':[],'reason':'no_obsolete_patterns_detected'}
    def evolve(self):
        reflection_engine.reflect_on_day()
        learning=learning_engine.learn()
        adaptation=adaptation_engine.adapt()
        evaluation=self.evaluate()
        archive=self.archive_candidates()
        event_bus.publish('EVOLUTION_EVALUATED',evaluation)
        evolution_history.record('EVOLUTION_EVALUATED',evaluation)
        return {'status':'evolving','evaluation':evaluation,'archive':archive,'adaptation':adaptation,'promoted_rules':learning.get('rule_candidates',[])}
evolution_engine=EvolutionEngine()
