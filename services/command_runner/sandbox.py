from .allowlist import get_command, list_allowed
from .audit import record


def dry_run(command_name: str):
    command = get_command(command_name)
    allowed = command is not None
    return record(command_name, {
        'allowed': allowed,
        'command': command,
        'dry_run': True,
        'available_commands': list_allowed(),
    })
