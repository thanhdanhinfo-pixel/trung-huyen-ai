from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from drive import (
    create_folder,
    create_google_doc,
    grant_permission,
    move_file,
    rename_file,
)

router = APIRouter(prefix="/drive/manage", tags=["Google Drive Management"])


class CreateFolderRequest(BaseModel):
    name: str = Field(..., min_length=1)
    parent_id: Optional[str] = None


class CreateDocRequest(BaseModel):
    name: str = Field(..., min_length=1)
    content: str = ""
    parent_id: Optional[str] = None


class MoveFileRequest(BaseModel):
    file_id: str = Field(..., min_length=1)
    new_parent_id: str = Field(..., min_length=1)


class RenameFileRequest(BaseModel):
    file_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class GrantPermissionRequest(BaseModel):
    file_id: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    role: str = "reader"


@router.post("/create-folder")
def create_folder_endpoint(req: CreateFolderRequest):
    try:
        return {
            "status": "ok",
            "action": "create_folder",
            "result": create_folder(name=req.name, parent_id=req.parent_id),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": "create_folder", "message": str(exc)},
        )


@router.post("/create-doc")
def create_doc_endpoint(req: CreateDocRequest):
    try:
        return {
            "status": "ok",
            "action": "create_google_doc",
            "result": create_google_doc(
                name=req.name,
                content=req.content,
                parent_id=req.parent_id,
            ),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": "create_google_doc", "message": str(exc)},
        )


@router.post("/move")
def move_file_endpoint(req: MoveFileRequest):
    try:
        return {
            "status": "ok",
            "action": "move_file",
            "result": move_file(file_id=req.file_id, new_parent_id=req.new_parent_id),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": "move_file", "message": str(exc)},
        )


@router.post("/rename")
def rename_file_endpoint(req: RenameFileRequest):
    try:
        return {
            "status": "ok",
            "action": "rename_file",
            "result": rename_file(file_id=req.file_id, name=req.name),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": "rename_file", "message": str(exc)},
        )


@router.post("/grant-permission")
def grant_permission_endpoint(req: GrantPermissionRequest):
    try:
        return {
            "status": "ok",
            "action": "grant_permission",
            "result": grant_permission(
                file_id=req.file_id,
                email=req.email,
                role=req.role,
            ),
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "action": "grant_permission", "message": str(exc)},
        )
