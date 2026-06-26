from system.reflection_engine import reflection_engine
from system.learning_engine import learning_engine
from system.adaptation_engine import adaptation_engine
from system.knowledge_graph import knowledge_graph
from system.event_bus import event_bus

class EvolutionEngine:
    def evolve(self):
        r=reflection_engine.reflect_on_day(); l=learning_engine.learn(); a=adaptation_engine.adapt(); k=knowledge_graph.snapshot()
        promoted=l.get('rule_candidates',[])
        event_bus.publish('EVOLUTION_CYCLE_COMPLETED',{'promoted':promoted})
        return {'status':'evolving','promoted_rules':promoted,'knowledge':k,'adaptation':a}

evolution_engine=EvolutionEngine()
