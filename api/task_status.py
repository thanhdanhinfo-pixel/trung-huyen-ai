from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix='/system/tasks', tags=['tasks'])

ACTIVE_TASKS = {
    'security-runtime-deploy': {
        'title': 'Deploy Security Runtime',
        'build_id': '074038cf-5aa3-4580-ac21-1f8b31273267',
        'started_at': '2026-07-02T05:14:13Z',
        'eta_seconds': 480,
        'cloud_run_delay_seconds': 120,
        'progress': 35,
        'current_step': 'docker build',
        'status': 'RUNNING',
    }
}


def enrich_task(task: dict) -> dict:
    enriched = dict(task)
    started_at = task.get('started_at')
    eta_seconds = task.get('eta_seconds')

    if started_at and isinstance(eta_seconds, (int, float)):
        try:
            started = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            remaining = max(0, int(eta_seconds - elapsed))
            enriched['remaining_seconds'] = remaining
        except Exception:
            enriched['remaining_seconds'] = eta_seconds

    return enriched


@router.get('/active')
def active_tasks():
    now = datetime.now(timezone.utc).isoformat()
    return {
        'server_time': now,
        'tasks': {
            key: enrich_task(value)
            for key, value in ACTIVE_TASKS.items()
        },
    }
