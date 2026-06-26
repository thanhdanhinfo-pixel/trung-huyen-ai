from typing import Any, Dict, List

from system import governance, self_healing, policy_engine


class RuleEngine:
    def evaluate(self) -> List[Dict[str, Any]]:
        rules = []
        consistency = governance.consistency_report()

        if consistency['status'] != 'ok':
            rules.append({
                'rule': 'registry_drift',
                'action': 'trigger_self_healing',
                'status': 'triggered'
            })

        policy = policy_engine.evaluate()
        if policy['violation_count'] > 0:
            rules.append({
                'rule': 'policy_violation',
                'action': 'deny_protected_changes',
                'status': 'triggered'
            })

        if not rules:
            rules.append({
                'rule': 'system_healthy',
                'action': 'none',
                'status': 'ok'
            })

        return rules

    def execute(self) -> Dict[str, Any]:
        rules = self.evaluate()
        executed = []

        for rule in rules:
            if rule['action'] == 'trigger_self_healing':
                from system import event_bus
                event_bus.publish('RULE_TRIGGERED', rule)
                executed.append(self_healing.auto_repair())

        return {
            'rules': rules,
            'executed_actions': executed,
            'count': len(executed)
        }


rule_engine = RuleEngine()
