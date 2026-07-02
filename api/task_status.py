from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix='/system/tasks', tags=['tasks'])

ACTIVE_TASKS = {
    'security-runtime-deploy': {
        'title': 'Deploy Security Runtime',
        'build_id': '074038cf-5aa3-4580-ac21-1f8b31273267',
        'started_at': '2026-07-02T05:14:13Z',
        'eta_seconds': 480,
        'current_step': 'docker build',
        'status': 'RUNNING',
    }
}


@router.get('/active')
def active_tasks():
    now = datetime.now(timezone.utc).isoformat()
    return {
        'server_time': now,
        'tasks': ACTIVE_TASKS,
    }
