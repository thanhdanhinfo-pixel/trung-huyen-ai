from system import event_bus, self_healing

class RuleEngineV2:
    def evaluate_runtime(self, worker_failed=False, backlog=0, boot_failed=False):
        actions=[]
        if worker_failed:
            actions.append('restart_worker')
        if backlog>100:
            actions.append('scale_workers')
        if boot_failed:
            actions.append('restore_last_healthy_snapshot')

        # RULE-020: Capability Denial Prohibition
        # Runtime must verify and attempt execution before declaring missing capabilities.
        actions.append('verify_capabilities_before_denial')

        return actions or ['system_nominal']

    def execute(self, **kwargs):
        actions=self.evaluate_runtime(**kwargs)
        for a in actions:
            event_bus.publish('RULE_V2_ACTION',{'action':a})
            if a=='restore_last_healthy_snapshot':
                self_healing.auto_repair()
        return {'actions':actions}

rule_engine_v2=RuleEngineV2()
