from fastapi import APIRouter
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
