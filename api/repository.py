from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.repository_manager import repository_manager

router = APIRouter(prefix="/repository", tags=["Quản lý Repository"])


class RepositoryPlanRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)


class RepositoryExecuteRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=20)
    import_file_limit: int = Field(default=50, ge=1, le=500)


@router.get("/status")
def repository_status():
    return repository_manager.status()


@router.post("/analyze")
def repository_analyze():
    return repository_manager.analyze()


@router.post("/plan")
def repository_plan(req: RepositoryPlanRequest):
    return repository_manager.make_plan(limit=req.limit)


@router.post("/preview")
def repository_preview(req: RepositoryPlanRequest):
    return repository_manager.preview(limit=req.limit)


@router.post("/execute")
def repository_execute(req: RepositoryExecuteRequest):
    return repository_manager.execute(
        limit=req.limit,
        import_file_limit=req.import_file_limit,
    )


@router.get("/verify")
def repository_verify():
    return repository_manager.verify()
