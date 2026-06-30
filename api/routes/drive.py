from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from config import DRIVE_FOLDER_ID
from drive import list_files, search_files

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
