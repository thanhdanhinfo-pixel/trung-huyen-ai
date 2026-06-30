from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Final

HIGH_RISK_ACTIONS: Final[set[str]] = {
    'shell_exec',
    'cloud_build_submit',
    'cloud_run_deploy',
    'github_create_file',
    'github_upsert_file',
    'patch_file',
    'move_file',
    'open_all_locks',
    'close_all_locks',
}

AUDIT_LOG_PATH = Path(os.getenv('HIGH_RISK_AUDIT_LOG', '/tmp/high_risk_actions_audit.jsonl'))


def is_high_risk_action(action_name: str) -> bool:
    return action_name in HIGH_RISK_ACTIONS


def _stable_hash(payload: Dict[str, Any]) -> str:
    try:
        raw = json.dumps(payload, sort_keys=True, default=str, ensure_ascii=False)
    except Exception:
        raw = str(payload)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def write_high_risk_audit(
    *,
    action_name: str,
    payload: Dict[str, Any] | None = None,
    result: Dict[str, Any] | None = None,
    actor: str = 'TRUNG_HUYEN_AI_OS',
    mode: str = 'runtime',
) -> Dict[str, Any]:
    payload = payload or {}
    result = result or {}

    event = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'actor': actor,
        'action': action_name,
        'risk': 'high' if is_high_risk_action(action_name) else 'normal',
        'payload_hash': _stable_hash(payload),
        'result_status': result.get('status'),
        'mode': mode,
        'revision': os.getenv('K_REVISION', ''),
        'service': os.getenv('K_SERVICE', ''),
    }

    try:
        AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG_PATH.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
    except Exception as exc:
        event['audit_write_error'] = f'{type(exc).__name__}: {exc}'

    return event
