from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from kernel.kernel import kernel
from services.repository_tree_loader import repository_tree_loader

router = APIRouter(prefix="/system-awareness", tags=["System Awareness"])


class RefreshSystemModelRequest(BaseModel):
    paths: List[str] | None = Field(default=None)
    files: List[Dict[str, Any]] | None = Field(default=None)


@router.get("/summary")
def system_awareness_summary():
    return {"status": "ok", "summary": kernel.system_summary(), "discovery": kernel.discovery_status()}


@router.get("/model")
def export_system_model():
    return {"status": "ok", "system_model": kernel.export_system_model()}


@router.get("/node/{node_id}")
def find_node(node_id: str):
    node = kernel.find_node(node_id)
    if not node:
        return {"status": "not_found", "node_id": node_id}
    return {"status": "ok", "node": node}


@router.get("/node/{node_id}/dependencies")
def node_dependencies(node_id: str):
    return {"status": "ok", **kernel.dependencies(node_id)}


@router.get("/node/{node_id}/dependents")
def node_dependents(node_id: str):
    return {"status": "ok", **kernel.dependents(node_id)}


@router.get("/node/{node_id}/impact")
def node_impact(node_id: str):
    return {"status": "ok", "impact": kernel.impact(node_id)}


@router.get("/impact/{node_id}")
def impact_alias(node_id: str):
    return {"status": "ok", "impact": kernel.impact(node_id)}


@router.post("/refresh")
def refresh_system_model(req: RefreshSystemModelRequest):
    if req.files:
        return kernel.refresh_system_model(files=req.files)

    if req.paths:
        try:
            loaded = repository_tree_loader.load(req.paths)
            if loaded.files:
                return kernel.refresh_system_model(files=loaded.files)
        except Exception:
            pass

    return kernel.refresh_system_model(paths=req.paths, files=req.files)
