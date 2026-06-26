from system import system_awareness, digital_twin, observability
class GovernanceLayer:
    def consistency_report(self):
        self_state=system_awareness.self_state(); registry=system_awareness.capability_registry(); twin=digital_twin.load(); issues=[]
        rv=registry.get('registry_metadata',{}).get('schema_version')
        if self_state.get('capability_sync',{}).get('registry_version')!=rv: issues.append('SELF_STATE capability_sync.registry_version mismatch')
        if twin.get('capabilities',{}).get('registry_version')!=rv: issues.append('DIGITAL_TWIN capabilities.registry_version mismatch')
        return {'status':'ok' if not issues else 'drift_detected','issue_count':len(issues),'issues':issues}
    def health_report(self): return {'governance':self.consistency_report(),'observability':observability.system_snapshot()}
governance=GovernanceLayer()
