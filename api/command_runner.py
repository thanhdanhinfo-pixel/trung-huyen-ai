from fastapi import APIRouter
from services.command_runner.allowlist import list_allowed
from services.command_runner.sandbox import dry_run

router = APIRouter(prefix='/command-runner', tags=['command-runner'])

@router.get('/status')
def status():
    return {
        'mode': 'dry-run',
        'shell_enabled': False,
        'allowed_commands': list_allowed(),
    }

@router.get('/dry-run/{command_name}')
def preview(command_name: str):
    return dry_run(command_name)
