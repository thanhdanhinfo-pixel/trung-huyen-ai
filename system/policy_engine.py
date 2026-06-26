from typing import Any, Dict, List
from system import governance

class PolicyEngine:
    RULES = {
        'require_system_awareness': 'system_awareness capability must exist',
        'require_digital_twin': 'digital_twin capability must exist',
        'require_registry_sync': 'SELF_STATE registry version must match CAPABILITY_REGISTRY'
    }

    def evaluate(self) -> Dict[str, Any]:
        violations: List[str] = governance.consistency_report().get('issues', [])
        return {
            'status': 'compliant' if not violations else 'violations_detected',
            'rules': self.RULES,
            'violations': violations,
            'violation_count': len(violations)
        }

    def can_apply_change(self, change_type: str) -> bool:
        return change_type not in {'identity','mission','core_architecture','founder_directive'}

policy_engine = PolicyEngine()
