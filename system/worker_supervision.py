class WorkerSupervision:
    def inspect(self):
        return {
            'status': 'supervising',
            'workers': {
                'evolution_worker': 'ready',
                'retention_worker': 'ready'
            }
        }

    def restart(self, worker_name: str):
        return {'worker': worker_name, 'action': 'restart_requested', 'status': 'accepted'}


worker_supervision = WorkerSupervision()
