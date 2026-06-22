from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

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
    sha: str | None = None
    message: str


def github_error_response(exc: Exception):
    """Return structured GitHub connector errors instead of unhandled 500s."""
    if isinstance(exc, requests.HTTPError):
        response = exc.response
        status_code = response.status_code if response is not None else 502
        try:
            detail = response.json() if response is not None else {}
        except Exception:
            detail = response.text if response is not None else str(exc)

        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "source": "github",
                "type": "GitHubHTTPError",
                "status_code": status_code,
                "detail": detail,
            },
        )

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "source": "github",
            "type": type(exc).__name__,
            "message": str(exc),
        },
    )


@router.get("/list")
def list_files(path: str = ""):
    try:
        return {
            "status": "ok",
            "path": path,
            "files": github_list_files(path),
        }
    except Exception as exc:
        return github_error_response(exc)


@router.post("/read")
def read_file(req: ReadFile):
    try:
        data = github_read_file(req.path)
        data["status"] = "ok"
        return data
    except Exception as exc:
        return github_error_response(exc)


@router.post("/update")
def update_file(req: UpdateFile):
    try:
        return github_update_file(
            req.path,
            req.content,
            req.sha,
            req.message,
        )
    except Exception as exc:
        return github_error_response(exc)
