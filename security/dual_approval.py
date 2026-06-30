from __future__ import annotations

import os
from typing import Final

HIGH_RISK_ACTIONS: Final[set[str]] = {
    'shell_exec',
    'cloud_build_submit',
    'cloud_run_deploy',
    'github_upsert_file',
    'patch_file',
    'move_file',
}


def approval_mode() -> str:
    return os.getenv('DUAL_APPROVAL_MODE', 'warn').lower()


def requires_dual_approval(action_name: str) -> bool:
    return action_name in HIGH_RISK_ACTIONS


def ensure_approved(action_name: str, approved: bool = False) -> None:
    if not requires_dual_approval(action_name):
        return

    mode = approval_mode()
    if mode == 'off':
        return

    if mode == 'warn' and not approved:
        print(f'[SECURITY][WARN] {action_name} executed without second approval')
        return

    if mode == 'enforce' and not approved:
        raise PermissionError(f'Dual approval required for {action_name}')
