from datetime import datetime
from system.evolution_worker import evolution_worker
from system.retention_worker import retention_worker

class SchedulerRuntime:
    def __init__(self):
        self._runs = []

    def run_cycle(self):
        result = {
            'time': datetime.utcnow().isoformat() + 'Z',
            'evolution': evolution_worker.run_once(),
            'retention': retention_worker.run_once(),
            'status': 'completed'
        }
        self._runs.append(result)
        return result

    def status(self):
        return {'status': 'ready', 'run_count': len(self._runs), 'last_run': self._runs[-1] if self._runs else None}


scheduler_runtime = SchedulerRuntime()
