from typing import Any, Dict, List
from system import governance
from system.bootstrap import boot
from system.digital_twin import digital_twin

class SelfHealing:
    def detect(self) -> Dict[str, Any]:
        return governance.consistency_report()

    def repair_plan(self) -> List[str]:
        report = self.detect()
        if report['status'] == 'ok':
            return [
                'Refresh persistent snapshot',
                'Synchronize digital twin health state'
            ]
        return governance.recommended_actions()

    def auto_repair(self) -> Dict[str, Any]:
        report = self.detect()

        if report['status'] == 'ok':
            boot()
            digital_twin.update_health('self_healing', 'healthy')
            return {
                'executed': True,
                'actions': self.repair_plan(),
                'status': 'auto_repaired'
            }

        return {
            'executed': False,
            'actions': governance.recommended_actions(),
            'status': 'manual_review_required',
            'issues': report.get('issues', [])
        }

self_healing = SelfHealing()
