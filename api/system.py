from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from services.system_service import self_test

router = APIRouter(
    prefix="/system",
    tags=["System"],
)

SYSTEM_STATE_FILES = [
    "system/BOOT_SEQUENCE.md",
    "system/TRUNG_HUYEN_AI_OS_PERSISTENT_IDENTITY.md",
    "system/SELF_STATE.yaml",
    "system/SYSTEM_MODEL.yaml",
    "system/CAPABILITY_REGISTRY.yaml",
    "system/TASK_REGISTRY.yaml",
    "system/MEMORY_LOG.md",
]


@router.get("/self-test")
def test():
    return self_test()


@router.get("/bootstrap")
def system_bootstrap():
    """
    Official bootstrap entrypoint for TRUNG_HUYEN_AI_OS.

    This endpoint is the single runtime bridge for loading system identity,
    self state, model, capability registry, task registry and memory log.
    Legacy bootstrap paths should not be used as the primary source of truth.
    """
    root = Path.cwd()
    files: dict[str, Any] = {}
    missing: list[str] = []

    for relative_path in SYSTEM_STATE_FILES:
        path = root / relative_path
        if not path.exists():
            missing.append(relative_path)
            files[relative_path] = {
                "status": "missing",
                "content": "",
            }
            continue

        files[relative_path] = {
            "status": "ok",
            "content": path.read_text(encoding="utf-8"),
        }

    return {
        "status": "ok" if not missing else "partial",
        "system": "TRUNG_HUYEN_AI_OS",
        "bootstrap_version": "1.0.0",
        "source_of_truth": "github:system/*",
        "boot_sequence": SYSTEM_STATE_FILES,
        "deprecated": [
            {
                "name": "workspace_load",
                "reason": "Legacy workspace path. Not the official system bootstrap.",
            },
            {
                "name": "workspace_bootstrap",
                "reason": "Drive workspace bootstrap. Superseded by /system/bootstrap for OS state.",
            },
        ],
        "files": files,
        "missing": missing,
        "next_action": "Use this endpoint before answering questions about system state, continuity, current work or operating context.",
    }


@router.get("/files")
def files():
    from drive import list_recursive
    return {
        "status": "ok",
        "files": list_recursive(),
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


@router.get("/runtime/diagnostic/version")
def runtime_diagnostic_version():
    from services.runtime_diagnostic import runtime_diagnostic
    return runtime_diagnostic.version()


@router.get("/runtime/diagnostic/github")
def runtime_diagnostic_github():
    from services.runtime_diagnostic import runtime_diagnostic
    return runtime_diagnostic.github_status()


@router.post("/runtime/diagnostic/github-write-selftest")
def runtime_diagnostic_github_write_selftest():
    from services.runtime_diagnostic import runtime_diagnostic
    return runtime_diagnostic.github_write_selftest()


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
    return health_runtime.last_report or {
        "status": "idle",
        "message": "No self-test has been executed yet.",
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
def runtime_execute(req: CreateTaskRequest):
    from services.ai_runtime import ai_runtime
    return ai_runtime.execute(
        title=req.title,
        worker=req.worker,
        priority=req.priority,
    )


class DriveCreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1)
    parent_id: Optional[str] = None


class DriveCreateDocRequest(BaseModel):
    name: str = Field(..., min_length=1)
    content: str = ""
    parent_id: Optional[str] = None


class DriveMoveRequest(BaseModel):
    file_id: str = Field(..., min_length=1)
    new_parent_id: str = Field(..., min_length=1)


class DriveRenameRequest(BaseModel):
    file_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


@router.post("/drive/create-folder")
def system_drive_create_folder(req: DriveCreateFolderRequest):
    from drive import create_folder
    return {
        "status": "ok",
        "action": "drive.create_folder",
        "result": create_folder(name=req.name, parent_id=req.parent_id),
    }


@router.post("/drive/create-doc")
def system_drive_create_doc(req: DriveCreateDocRequest):
    from drive import create_google_doc
    return {
        "status": "ok",
        "action": "drive.create_doc",
        "result": create_google_doc(
            name=req.name,
            content=req.content,
            parent_id=req.parent_id,
        ),
    }


@router.post("/drive/move")
def system_drive_move(req: DriveMoveRequest):
    from drive import move_file
    return {
        "status": "ok",
        "action": "drive.move",
        "result": move_file(file_id=req.file_id, new_parent_id=req.new_parent_id),
    }


@router.post("/drive/rename")
def system_drive_rename(req: DriveRenameRequest):
    from drive import rename_file
    return {
        "status": "ok",
        "action": "drive.rename",
        "result": rename_file(file_id=req.file_id, name=req.name),
    }


class DeveloperPatchRequest(BaseModel):
    files: list[dict[str, Any]] = Field(default_factory=list)
    message: str = "Developer runtime patch"
    commit: bool = False


class DeveloperBatchRequest(BaseModel):
    operations: list[dict[str, Any]] = Field(default_factory=list)
    message: str = "Developer runtime batch"
    commit: bool = False


class DeveloperVerifyRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)


@router.get("/developer/status")
def developer_status():
    from services.developer_runtime import developer_runtime
    return developer_runtime.status()


@router.post("/developer/patch")
def developer_patch(req: DeveloperPatchRequest):
    from services.developer_runtime import developer_runtime
    return developer_runtime.patch(
        files=req.files,
        message=req.message,
        commit=req.commit,
    )


@router.post("/developer/commit")
def developer_commit(req: DeveloperBatchRequest):
    from services.developer_runtime import developer_runtime
    return developer_runtime.batch(
        operations=req.operations,
        message=req.message,
        commit=req.commit,
    )


@router.post("/developer/verify")
def developer_verify(req: DeveloperVerifyRequest):
    from services.developer_runtime import developer_runtime
    return developer_runtime.verify(paths=req.paths)


@router.post("/developer/rollback")
def developer_rollback():
    from services.developer_runtime import developer_runtime
    return developer_runtime.rollback()
