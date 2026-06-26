from typing import Any, Dict, List
from system import governance

class PolicyEngine:
    LIFECYCLE = ['PROPOSED','EXPERIMENTAL','ACTIVE','DEPRECATED','REMOVED']

    RULES = {
        'require_system_awareness':'system_awareness capability must exist',
        'require_digital_twin':'digital_twin capability must exist',
        'require_registry_sync':'SELF_STATE registry version must match CAPABILITY_REGISTRY'
    }

    def evaluate(self)->Dict[str,Any]:
        violations = governance.consistency_report().get('issues',[])
        return {
            'status':'compliant' if not violations else 'violations_detected',
            'violation_count':len(violations),
            'violations':violations,
            'lifecycle_states':self.LIFECYCLE,
            'rollback_enabled':True,
            'approval_required_for':['identity','mission','core_architecture']
        }

    def approval_workflow(self, change_type:str)->Dict[str,str]:
        return {
            'change_type':change_type,
            'status':'founder_approval_required' if change_type in {'identity','mission','core_architecture'} else 'auto_approved'
        }

    def rollback_policy(self)->Dict[str,Any]:
        return {'enabled':True,'strategy':'restore_last_healthy_snapshot'}

policy_engine = PolicyEngine()
