from datetime import datetime, timezone

from fastapi import APIRouter

from services.task_runtime import task_runtime

router = APIRouter(prefix='/system/tasks', tags=['tasks'])


@router.get('/active')
def active_tasks():
    return {
        'server_time': datetime.now(timezone.utc).isoformat(),
        'tasks': task_runtime.active(),
    }


@router.post('/demo/start')
def demo_start_task():
    return task_runtime.start(
        task_id='demo-countdown',
        title='Demo Countdown Task',
        eta_seconds=300,
        current_step='Khởi tạo kiểm thử',
        cloud_run_delay_seconds=90,
    )


@router.post('/demo/complete')
def demo_complete_task():
    return task_runtime.complete('demo-countdown')
