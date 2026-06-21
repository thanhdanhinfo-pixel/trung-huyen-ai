from fastapi import APIRouter

from services.workspace_service import load_workspace

router = APIRouter(
    prefix="/workspace",
    tags=["Workspace"],
)


@router.get("/load")
def workspace_load():

    return load_workspace()
