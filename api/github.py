from fastapi import APIRouter
from pydantic import BaseModel

from services.github_service import (
    github_list_files,
    github_read_file,
    github_update_file,
)

router = APIRouter(prefix="/github", tags=["GitHub"])


class ReadFile(BaseModel):
    path: str


class UpdateFile(BaseModel):
    path: str
    content: str
    sha: str
    message: str


@router.get("/list")
def list_files(path: str = ""):
    return github_list_files(path)


@router.post("/read")
def read_file(req: ReadFile):
    return github_read_file(req.path)


@router.post("/update")
def update_file(req: UpdateFile):
    return github_update_file(
        req.path,
        req.content,
        req.sha,
        req.message,
    )
