from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.background_loop import background_loop
from services.execution_queue import execution_queue
from services.worker_registry import worker_registry
from services.worker_runner import worker_runner

router = APIRouter(prefix="/worker", tags=["AI Worker"])


class EnqueueTaskRequest(BaseModel):
    title: str = Field(..., min_length=1)
    capability: str = Field(..., min_length=1)
    owner: str = "ai_ceo"
    priority: int = Field(default=3, ge=1, le=10)
    payload: dict[str, Any] = Field(default_factory=dict)


@router.get("/status")
def worker_status():
    return {
        "status": "ok",
        "registry": worker_registry.status(),
        "runner": worker_runner.status(),
        "background": background_loop.status(),
        "queue": execution_queue.status(),
    }


@router.post("/bootstrap")
def worker_bootstrap():
    return worker_runner.bootstrap()


@router.post("/enqueue")
def worker_enqueue(req: EnqueueTaskRequest):
    return worker_runner.enqueue_task(
        title=req.title,
        capability=req.capability,
        owner=req.owner,
        priority=req.priority,
        payload=req.payload,
    )


@router.post("/run-once")
def worker_run_once(capability: str | None = None):
    return worker_runner.run_once(capability=capability)


@router.post("/run-batch")
def worker_run_batch(limit: int = 5, capability: str | None = None):
    return worker_runner.run_batch(limit=limit, capability=capability)


@router.post("/tick")
def worker_tick(limit: int = 5, capability: str | None = None):
    return background_loop.tick(limit=limit, capability=capability)


@router.post("/enable")
def worker_enable():
    return background_loop.enable()


@router.post("/disable")
def worker_disable():
    return background_loop.disable()


@router.get("/history")
def worker_history(limit: int = 20):
    return background_loop.recent(limit=limit)


@router.get("/tasks")
def worker_tasks(status: str | None = None, limit: int = 100):
    return execution_queue.list(status=status, limit=limit)
