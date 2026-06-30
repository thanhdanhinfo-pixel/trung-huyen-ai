from __future__ import annotations

import os

BLOCKED_ACTIONS = {
    'shell_exec',
    'github_create_file',
    'github_upsert_file',
    'patch_file',
    'cloud_build_submit',
    'cloud_run_deploy',
    'move_file',
}


def emergency_mode_enabled() -> bool:
    return os.getenv('GLOBAL_EMERGENCY_MODE', 'false').lower() == 'true'


def ensure_action_allowed(action_name: str) -> None:
    if emergency_mode_enabled() and action_name in BLOCKED_ACTIONS:
        raise PermissionError(
            f'Action {action_name} is blocked because GLOBAL_EMERGENCY_MODE=true'
        )
