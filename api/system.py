from fastapi import APIRouter
from pydantic import BaseModel
from services.system_service import self_test

router=APIRouter(prefix="/system",tags=["System"])

@router.get("/self-test")
def test(): return self_test()

@router.get("/runtime/self-test")
def runtime_self_test():
    from services.health_runtime import health_runtime
    return health_runtime.self_test()

@router.post("/runtime/self-test/run")
def runtime_self_test_run():
    from services.health_runtime import health_runtime
    return health_runtime.self_test()

@router.get("/runtime/self-test/latest")
def runtime_self_test_latest():
    from services.health_runtime import health_runtime
    return health_runtime.last_report or {"status":"idle","message":"No self-test has been executed yet."}

@router.get("/runtime/status")
def ai_runtime_status():
    from services.ai_runtime import ai_runtime
    return ai_runtime.status()

@router.get("/runtime/tasks")
def ai_runtime_tasks():
    from services.ai_runtime import ai_runtime
    return {"status":"ok","tasks":ai_runtime.list_tasks()}

class CreateTaskRequest(BaseModel):
    title:str
    worker:str="orchestrator"
    priority:int=3

@router.post("/runtime/tasks")
def create_runtime_task(req:CreateTaskRequest):
    from services.ai_runtime import ai_runtime
    return ai_runtime.add_task(title=req.title,worker=req.worker,priority=req.priority)

@router.post("/runtime/execute")
def runtime_execute(req:CreateTaskRequest):
    from services.ai_runtime import ai_runtime
    return ai_runtime.execute(title=req.title,worker=req.worker,priority=req.priority)
