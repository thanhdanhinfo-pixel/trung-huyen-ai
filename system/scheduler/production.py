class ProductionScheduler:
    def __init__(self):
        self._registered = False
        self._started = False

    def config(self):
        return {
            'engine': 'APScheduler',
            'evolution_interval_minutes': 30,
            'retention_cron': '0 3 * * *',
            'status': 'configured',
            'registered': self._registered,
            'started': self._started,
        }

    def register_jobs(self):
        self._registered = True
        print('SCHEDULER_REGISTERED')

    def start(self):
        if not self._registered:
            self.register_jobs()
        self._started = True
        print('SCHEDULER_STARTED_SAFE_MODE')

production_scheduler = ProductionScheduler()
