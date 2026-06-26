from __future__ import annotations

from typing import Any, Dict, List

from system import system_awareness, digital_twin, observability


class GovernanceLayer:
    """Consistency and drift checks for TRUNG_HUYEN_AI_OS."""

    def consistency_report(self) -> Dict[str, Any]:
        self_state = system_awareness.self_state()
        registry = system_awareness.capability_registry()
        twin = digital_twin.load()

        issues: List[str] = []

        registry_version = registry.get('registry_metadata', {}).get('schema_version')
        synced_version = self_state.get('capability_sync', {}).get('registry_version')
        if registry_version != synced_version:
            issues.append('SELF_STATE capability_sync.registry_version does not match CAPABILITY_REGISTRY schema_version')

        twin_registry_version = twin.get('capabilities', {}).get('registry_version')
        if twin_registry_version != registry_version:
            issues.append('DIGITAL_TWIN capabilities.registry_version does not match CAPABILITY_REGISTRY schema_version')

        if not registry.get('capability_groups', {}).get('system_awareness'):
            issues.append('CAPABILITY_REGISTRY missing system_awareness capability')

        if not registry.get('capability_groups', {}).get('digital_twin'):
            issues.append('CAPABILITY_REGISTRY missing digital_twin capability')

        return {
            'status': 'ok' if not issues else 'drift_detected',
            'issue_count': len(issues),
            'issues': issues,
        }

    def health_report(self) -> Dict[str, Any]:
        return {
            'governance': self.consistency_report(),
            'observability': observability.system_snapshot(),
        }

    def recommended_actions(self) -> List[str]:
        report = self.consistency_report()
        if report['status'] == 'ok':
            return ['No corrective action required']
        return [
            'Resynchronize SELF_STATE capability_sync',
            'Update DIGITAL_TWIN registry metadata',
            'Review CAPABILITY_REGISTRY capability groups',
        ]


governance = GovernanceLayer()
