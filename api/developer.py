from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Developer Gateway"])


class DeveloperExecuteRequest(BaseModel):
    action: str
    payload: dict[str, Any] = {}


@router.post("/developer/execute")
def developer_execute(req: DeveloperExecuteRequest):
    if req.action == "github.status":
        from services.github_runtime import github_runtime
        return github_runtime.status()

    if req.action == "github.read":
        from services.github_runtime import github_runtime
        return github_runtime.read_file(req.payload.get("path", ""))

    if req.action == "github.patch":
        from services.github_runtime import github_runtime
        return github_runtime.patch_file(
            path=req.payload.get("path", ""),
            operations=req.payload.get("operations", []),
            message=req.payload.get("message", "Developer Gateway patch"),
            commit=bool(req.payload.get("commit", False)),
        )

    return {
        "status": "error",
        "message": f"Unsupported action: {req.action}",
    }
