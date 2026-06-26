from datetime import datetime
from system.evolution_engine import evolution_engine

class EvolutionWorker:
    def run_once(self):
        result=evolution_engine.evolve()
        return {
            'time': datetime.utcnow().isoformat()+'Z',
            'status':'completed',
            'result':result
        }

evolution_worker=EvolutionWorker()
