from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import yaml

from system import governance
from system.bootstrap import boot
from system.digital_twin import digital_twin

BASE = Path(__file__).parent
SELF_STATE_PATH = BASE / 'SELF_STATE.yaml'
CAPABILITY_REGISTRY_PATH = BASE / 'CAPABILITY_REGISTRY.yaml'
DIGITAL_TWIN_PATH = BASE / 'DIGITAL_TWIN.yaml'


class SelfHealing:
    """Safe self-healing layer.

    v2 can auto-correct metadata drift only. It does not rewrite architecture,
    capability definitions, mission, identity, or source-of-truth semantics.
    """

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _save_yaml(self, path: Path, data: Dict[str, Any]) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    def detect(self) -> Dict[str, Any]:
        return governance.consistency_report()

    def repair_plan(self) -> List[str]:
        report = self.detect()
        if report['status'] == 'ok':
            return [
                'Refresh persistent snapshot',
                'Synchronize digital twin health state'
            ]
        return [
            'Synchronize SELF_STATE capability_sync.registry_version',
            'Synchronize DIGITAL_TWIN capabilities.registry_version',
            'Refresh persistent snapshot',
            'Mark self_healing metadata_auto_corrected'
        ]

    def auto_correct_metadata(self) -> Dict[str, Any]:
        registry = self._load_yaml(CAPABILITY_REGISTRY_PATH)
        self_state = self._load_yaml(SELF_STATE_PATH)
        twin = self._load_yaml(DIGITAL_TWIN_PATH)

        registry_version = registry.get('registry_metadata', {}).get('schema_version')
        today = str(date.today())
        changed: List[str] = []

        capability_sync = self_state.setdefault('capability_sync', {})
        if capability_sync.get('registry_version') != registry_version:
            capability_sync['registry_version'] = registry_version
            capability_sync['synchronized'] = True
            capability_sync['synchronized_at'] = today
            capability_sync['source'] = 'system/CAPABILITY_REGISTRY.yaml'
            self_state['last_updated'] = today
            changed.append('SELF_STATE.capability_sync')

        twin_capabilities = twin.setdefault('capabilities', {})
        if twin_capabilities.get('registry_version') != registry_version:
            twin_capabilities['registry_version'] = registry_version
            twin_capabilities['source'] = 'system/CAPABILITY_REGISTRY.yaml'
            twin['last_updated'] = today
            changed.append('DIGITAL_TWIN.capabilities')

        twin_health = twin.setdefault('health', {})
        if twin_health.get('self_healing') != 'metadata_auto_corrected':
            twin_health['self_healing'] = 'metadata_auto_corrected'
            twin['last_updated'] = today
            changed.append('DIGITAL_TWIN.health.self_healing')

        if changed:
            self._save_yaml(SELF_STATE_PATH, self_state)
            self._save_yaml(DIGITAL_TWIN_PATH, twin)

        return {
            'changed': changed,
            'changed_count': len(changed),
            'registry_version': registry_version,
        }

    def auto_repair(self) -> Dict[str, Any]:
        before = self.detect()

        metadata_result = self.auto_correct_metadata()
        boot()
        digital_twin.update_health('self_healing', 'healthy')

        after = self.detect()

        from system import event_bus
        status = 'auto_repaired' if after['status'] == 'ok' else 'partial_repair_manual_review_required'
        event_bus.publish('SELF_HEALING_EXECUTED', {'status': status})

        return {
            'executed': True,
            'status': status,
            'before': before,
            'after': after,
            'metadata': metadata_result,
            'actions': self.repair_plan(),
        }


self_healing = SelfHealing()
