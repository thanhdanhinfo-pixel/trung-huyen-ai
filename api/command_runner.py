from fastapi import APIRouter, Header, HTTPException

from config import MCP_API_KEY
from services.command_runner.allowlist import list_allowed
from services.command_runner.sandbox import dry_run, execute

router = APIRouter(prefix='/command-runner', tags=['command-runner'])


def _require_api_key(x_api_key: str | None):
    if not MCP_API_KEY:
        raise HTTPException(status_code=503, detail='MCP_API_KEY not configured')
    if x_api_key != MCP_API_KEY:
        raise HTTPException(status_code=401, detail='invalid api key')


@router.get('/status')
def status():
    return {
        'mode': 'allowlist-execute',
        'shell_enabled': False,
        'allowed_commands': list_allowed(),
        'execute_requires_x_api_key': True,
    }


@router.get('/dry-run/{command_name}')
def preview(command_name: str):
    return dry_run(command_name)


@router.post('/execute/{command_name}')
def run(command_name: str, timeout_seconds: int | None = None, x_api_key: str | None = Header(default=None)):
    _require_api_key(x_api_key)
    return execute(command_name, timeout_seconds)
