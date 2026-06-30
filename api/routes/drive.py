from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import DRIVE_FOLDER_ID
from drive import (
    list_files,
    search_files,
    read_file_content,
    search_and_read,
    find_file_by_path,
    read_folder,
    get_path_index,
)

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


@router.post("/search-read")
def drive_search_read(req: SearchReadRequest):
    try:
        files = search_and_read(
            q=req.q,
            limit=req.limit,
            max_chars_per_file=req.max_chars_per_file,
        )

        return {
            "status": "ok",
            "query": req.q,
            "files": files,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )


@router.get("/read-path")
def drive_read_path(path: str):
    try:
        item = find_file_by_path(path)
        if not item:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Path not found", "path": path},
            )

        content = read_file_content(item["id"], item.get("mimeType"))
        return {
            "status": "ok",
            "path": path,
            "file_id": item["id"],
            "name": item.get("name"),
            "content_length": len(content),
            "content": content,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "type": type(exc).__name__, "message": str(exc)},
        )


@router.get("/list-path")
def drive_list_path(path: str = "/"):
    try:
        return {"status": "ok", "path": path, "files": read_folder(path)}
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )


@router.get("/root")
def drive_root(limit: int = Query(default=200, ge=1, le=500)):
    try:
        files = list_files(limit=limit)
        return {
            "status": "ok",
            "root": "DRIVE_FOLDER_ID",
            "folder_limited": bool(DRIVE_FOLDER_ID),
            "entries": len(files),
            "files": files,
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@router.get("/tree")
def drive_tree(path: str = "/", limit: int = Query(default=200, ge=1, le=500)):
    try:
        if path == "/":
            files = list_files(limit=limit)
        else:
            files = read_folder(path)
        return {"status": "ok", "path": path, "tree": files}
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@router.get("/audit")
def drive_audit(limit: int = Query(default=200, ge=1, le=500)):
    try:
        files = list_files(limit=limit)
        folders = [
            f for f in files
            if f.get("mimeType") == "application/vnd.google-apps.folder"
        ]
        names = [f.get("name", "") for f in folders]
        all_names = [f.get("name", "") for f in files]
        return {
            "status": "ok",
            "source": "DRIVE_FOLDER_ID",
            "folder_limited": bool(DRIVE_FOLDER_ID),
            "top_level_count": len(names),
            "top_level_folders": names,
            "all_entries_count": len(all_names),
            "all_entries": all_names,
            "recommended_domains": {
                "academy": [n for n in names if "academy" in n.lower() or "học viện" in n.lower()],
                "projects": [n for n in names if "project" in n.lower() or "dự án" in n.lower() or "ai" in n.lower()],
                "strategy": [n for n in names if "strategy" in n.lower() or "chiến lược" in n.lower()],
                "global_memory": [n for n in names if "bộ não" in n.lower() or "memory" in n.lower() or "global" in n.lower()],
            },
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})


@router.post("/rebuild-index")
def rebuild_drive_index():
    try:
        index = get_path_index(force_refresh=True)
        return {
            "status": "ok",
            "entries": len(index),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(exc)},
        )
