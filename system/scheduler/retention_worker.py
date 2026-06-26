from datetime import datetime
from system.event_retention import event_retention
class RetentionWorker:
    def run_once(self):
        return {'time':datetime.utcnow().isoformat()+'Z','policy':event_retention.policy(),'status':'dry_run_completed'}
retention_worker=RetentionWorker()
