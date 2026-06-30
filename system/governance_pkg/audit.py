from datetime import datetime
from system.policy_engine import policy_engine
from system.rule_engine import rule_engine
class GovernanceAudit: 
    def snapshot(self):
        return {'timestamp':datetime.utcnow().isoformat()+'Z','policies':policy_engine.evaluate(),'rules':rule_engine.evaluate()}
governance_audit=GovernanceAudit()
