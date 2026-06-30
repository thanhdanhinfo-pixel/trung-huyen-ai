from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import DRIVE_FOLDER_ID
from drive import list_files, search_files, read_file_content, search_and_read

router = APIRouter(prefix="/drive", tags=["drive"])


class SearchReadRequest(BaseModel):
    q: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    max_chars_per_file: int = Field(default=6000, ge=1000, le=20000)


@router.get("/files")
def drive_files(limit: int = Query(default=50, ge=1, le=200)):
    try:
        return {
            "status": "ok",
            "folder_limited": bool(DRIVE_FOLDER_ID),
            "files": list_files(limit=limit),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )


@router.get("/search")
def drive_search(q: str, limit: int = Query(default=20, ge=1, le=200)):
    try:
        files = search_files(q=q, limit=limit)
        return {
            "status": "ok",
            "query": q,
            "files": files,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )


@router.get("/read")
def drive_read(file_id: str):
    try:
        content = read_file_content(file_id=file_id)
        return {
            "status": "ok",
            "file_id": file_id,
            "content_length": len(content),
            "content": content,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )
