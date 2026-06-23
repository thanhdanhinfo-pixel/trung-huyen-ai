from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.kernel import kernel

router = APIRouter(prefix="/kernel", tags=["Kernel"])


class RegisterPluginRequest(BaseModel):
    name: str = Field(..., min_length=1)
    capability: str = Field(..., min_length=1)
    owner: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PublishEventRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class StateRequest(BaseModel):
    key: str = Field(..., min_length=1)
    value: Any
    source: str = "kernel"


@router.get("/status")
def kernel_status():
    return kernel.status()


@router.post("/bootstrap")
def kernel_bootstrap():
    return kernel.bootstrap()


@router.get("/plugins")
def kernel_plugins(capability: str | None = None):
    return kernel.list_plugins(capability=capability)


@router.post("/plugins/register")
def kernel_register_plugin(req: RegisterPluginRequest):
    return kernel.register_plugin(
        name=req.name,
        capability=req.capability,
        owner=req.owner,
        metadata=req.metadata,
    )


@router.post("/plugins/unregister/{name}")
def kernel_unregister_plugin(name: str):
    return kernel.unregister_plugin(name)


@router.post("/events/publish")
def kernel_publish_event(req: PublishEventRequest):
    return kernel.publish(
        topic=req.topic,
        source=req.source,
        payload=req.payload,
    )


@router.get("/events/recent")
def kernel_recent_events(limit: int = 50):
    return kernel.recent_events(limit=limit)


@router.post("/state")
def kernel_set_state(req: StateRequest):
    return kernel.set_state(key=req.key, value=req.value, source=req.source)


@router.get("/state")
def kernel_get_state(key: str | None = None):
    return kernel.get_state(key=key)
