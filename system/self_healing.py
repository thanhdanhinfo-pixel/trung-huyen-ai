from typing import Any, Dict, List
from system import governance

class SelfHealing:
    def detect(self) -> Dict[str, Any]:
        return governance.consistency_report()

    def repair_plan(self) -> List[str]:
        report = self.detect()
        return ['System is healthy'] if report['status']=='ok' else governance.recommended_actions()

    def auto_repair(self) -> Dict[str, Any]:
        report = self.detect()
        return {
            'executed': report['status'] != 'ok',
            'actions': self.repair_plan(),
            'status': 'noop' if report['status']=='ok' else 'manual_review_required'
        }

self_healing = SelfHealing()
