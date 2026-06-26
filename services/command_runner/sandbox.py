import subprocess
from typing import Any, Dict

from .allowlist import get_command, list_allowed
from .audit import record
from .timeout import normalize_timeout


def dry_run(command_name: str):
    command = get_command(command_name)
    allowed = command is not None
    return record(command_name, {
        'allowed': allowed,
        'command': command,
        'dry_run': True,
        'available_commands': list_allowed(),
    })


def execute(command_name: str, timeout_seconds: int | None = None) -> Dict[str, Any]:
    command = get_command(command_name)
    if command is None:
        return record(command_name, {
            'allowed': False,
            'executed': False,
            'available_commands': list_allowed(),
        })

    timeout = normalize_timeout(timeout_seconds)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            check=False,
        )
        return record(command_name, {
            'allowed': True,
            'executed': True,
            'returncode': result.returncode,
            'stdout': result.stdout[-4000:],
            'stderr': result.stderr[-4000:],
            'timeout_seconds': timeout,
        })
    except subprocess.TimeoutExpired as exc:
        return record(command_name, {
            'allowed': True,
            'executed': False,
            'timeout': True,
            'timeout_seconds': timeout,
            'message': str(exc),
        })
