from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from kernel.kernel import kernel


router = APIRouter(prefix="/planner", tags=["Planner"])


class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=1)
    target: str | None = None
    context: Dict[str, Any] = Field(default_factory=dict)


@router.post("/plan")
def create_plan(req: PlanRequest):
    return kernel.plan(goal=req.goal, target=req.target, context=req.context)


@router.post("/next")
def plan_next_action():
    return kernel.plan_next_action()
