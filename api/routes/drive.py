from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from config import DRIVE_FOLDER_ID
from drive import list_files, search_files, read_file_content

router = APIRouter(prefix="/drive", tags=["drive"])


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
