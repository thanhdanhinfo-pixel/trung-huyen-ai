from fastapi import APIRouter
from system.scheduler_runtime import scheduler_runtime
from system.worker_supervision import worker_supervision
from system.runtime_bootstrap import runtime_bootstrap

router=APIRouter(prefix='/system',tags=['system-scheduler'])
@router.get('/scheduler')
def scheduler_status():
    return {'runtime': runtime_bootstrap.scheduler_state(),'cycles':scheduler_runtime.status()}
@router.post('/scheduler/run')
def scheduler_run(): return scheduler_runtime.run_cycle()
@router.get('/supervision')
def supervision(): return worker_supervision.inspect()
