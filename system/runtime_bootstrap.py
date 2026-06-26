import os

from system.production_scheduler import production_scheduler

class RuntimeBootstrap:
    def scheduler_state(self):
        enabled = os.getenv('SCHEDULER_ENABLED','false').lower() == 'true'
        cfg = production_scheduler.config()
        return {
            'enabled': enabled,
            'engine': cfg['engine'],
            'status': 'running' if enabled else 'disabled'
        }

runtime_bootstrap = RuntimeBootstrap()
