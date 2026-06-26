from fastapi import APIRouter

router = APIRouter(prefix='/system-status', tags=['system-status'])

@router.get('')
def unified_system_status():
    return {
        'cloud_run': True,
        'boot': {'enabled': True, 'mode': 'safe'},
        'scheduler': {'enabled': True, 'mode': 'safe'},
        'system_runtime': {'enabled': True, 'mode': 'safe'},
        'digital_twin': {'enabled': True, 'mode': 'safe'},
        'graph': {'enabled': True, 'mode': 'safe'},
        'advanced_rag': {'enabled': True, 'mode': 'safe'},
        'copy_move': {'enabled': True, 'mode': 'foundation'},
        'command_runner': {'enabled': True, 'mode': 'dry-run'},
        'integrations': {
            'drive': True,
            'github': True,
            'openai': True,
            'qdrant': True,
            'mcp': True,
        },
        'recovery_state': 'stable',
        'system': 'TRUNG_HUYEN_AI_OS'
    }
