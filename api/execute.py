from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["Execution"])


class ExecuteTask(BaseModel):
    type: str = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict)


class ExecuteRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    tasks: List[ExecuteTask] = Field(default_factory=list)
    approved: bool = False


@router.post("/execute")
def execute(req: ExecuteRequest):
    return {
        "status": "accepted",
        "goal": req.goal,
        "approved": req.approved,
        "task_count": len(req.tasks),
        "tasks": [task.model_dump() for task in req.tasks],
        "message": "Execution API is online. Worker execution will be attached next."
    }
