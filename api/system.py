from fastapi import APIRouter
from pydantic import BaseModel
from services.system_service import self_test

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

@router.get("/self-test")
def test():
    return self_test()

@router.get("/files")
def files():
    from drive import list_recursive
    return {
        "status": "ok",
        "files": list_recursive()
    }

@router.get("/tree")
def tree():
    from drive import list_recursive
    files = list_recursive()
    return {
        "status": "ok",
        "count": len(files),
        "files": [
            {
                "name": f.get("name"),
                "path": f.get("path"),
                "mimeType": f.get("mimeType"),
            }
            for f in files
        ],
    }

@router.get("/runtime/health")
def runtime_health_check():
    from runtime_health import runtime_health
    from services.github_runtime import github_runtime

    runtime_health.check("github", lambda: github_runtime.status())

    def drive_check():
        from drive import list_files
        files = list_files(limit=1)
        return {"reachable": True, "sample_count": len(files)}

    runtime_health.check("drive", drive_check)

    def qdrant_check():
        from vectordb import client, COLLECTION_NAME, ensure_collection
        ensure_collection()
        result = client.count(collection_name=COLLECTION_NAME, exact=True)
        return {"reachable": True, "count": result.count}

    runtime_health.check("qdrant", qdrant_check)
    runtime_health.check("runtime", lambda: {"reachable": True})

    return runtime_health.status()
@router.get("/runtime/status")
def ai_runtime_status():
    from services.ai_runtime import ai_runtime
    return ai_runtime.status()


@router.get("/runtime/tasks")
def ai_runtime_tasks():
    from services.ai_runtime import ai_runtime
    return {
        "status": "ok",
        "tasks": ai_runtime.list_tasks(),
    }
    

class CreateTaskRequest(BaseModel):
    title: str
    worker: str = "orchestrator"
    priority: int = 3


@router.post("/runtime/tasks")
def create_runtime_task(req: CreateTaskRequest):
    from services.ai_runtime import ai_runtime
    return ai_runtime.add_task(
        title=req.title,
        worker=req.worker,
        priority=req.priority,
    )
@router.post("/runtime/execute")
def runtime_execute():
    return {
        "status": "ok",
        "message": "Execution API ready"
    }
