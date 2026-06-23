from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.workflow_engine import workflow_engine

router = APIRouter(tags=["Developer Gateway"])


class DeveloperExecuteRequest(BaseModel):
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False
    auto_run: bool = True


@router.post("/developer/execute")
def developer_execute(req: DeveloperExecuteRequest):
    return workflow_engine.submit(
        action=f"developer.{req.action}",
        payload=req.payload,
        requires_approval=req.requires_approval,
        auto_run=req.auto_run,
    )


@router.get("/developer/workflow/status")
def developer_workflow_status():
    return workflow_engine.status()


@router.get("/developer/workflow/tasks")
def developer_workflow_tasks():
    return {
        "status": "ok",
        "tasks": workflow_engine.queue(),
    }
