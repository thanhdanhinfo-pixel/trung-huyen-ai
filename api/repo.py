from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.repo_refactor import repo_refactor

router = APIRouter(prefix="/repo", tags=["Repository Refactor"])


class RefactorPreviewRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=50)


class RefactorExecuteRequest(BaseModel):
    limit: int = Field(default=3, ge=1, le=20)
    import_file_limit: int = Field(default=50, ge=1, le=500)


@router.get("/status")
def repo_status():
    return repo_refactor.status()


@router.get("/history")
def repo_history():
    return {"status": "ok", "history": repo_refactor.history()}


@router.post("/analyze")
def repo_analyze():
    return repo_refactor.analyze()


@router.get("/move-plan")
def repo_move_plan(limit: int = 10):
    return repo_refactor.move_plan(limit=limit)


@router.post("/refactor/preview")
def repo_refactor_preview(req: RefactorPreviewRequest):
    return repo_refactor.preview(limit=req.limit)


@router.post("/refactor/execute")
def repo_refactor_execute(req: RefactorExecuteRequest):
    return repo_refactor.execute(
        limit=req.limit,
        import_file_limit=req.import_file_limit,
    )


@router.post("/refactor/verify")
def repo_refactor_verify():
    return repo_refactor.verify()
