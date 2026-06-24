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

@router.get('/summary')
def system_awareness_summary():
    return {'status':'ok','summary':kernel.system_summary(),'discovery':kernel.discovery_status()}

@router.get('/model')
def export_system_model():
    return {'status':'ok','system_model':kernel.export_system_model()}

@router.get('/graph')
def architecture_graph():
    model = kernel.export_system_model()
    nodes=[]; edges=[]
    for node_id,node in model.get('nodes',{}).items():
        nodes.append({'id':node_id,'label':node.get('name') or node_id,'type':node.get('type'),'status':node.get('status'),'owner':node.get('owner'),'role':node.get('role')})
    for i,r in enumerate(model.get('relationships',[])):
        if r.get('source') and r.get('target'):
            edges.append({'id':f'e-{i}','source':r.get('source'),'target':r.get('target'),'label':r.get('relation')})
    return {'status':'ok','summary':model.get('summary',{}),'nodes':nodes,'edges':edges}

@router.get('/recommendations')
def architecture_recommendations():
    model = kernel.export_system_model()
    nodes = model.get('nodes', {})
    recommendations = []
    central = []

    for node_id, node in nodes.items():
        deps = node.get('dependencies', [])
        if not deps:
            recommendations.append({'type':'orphan_candidate','node':node_id,'message':'Node has no declared dependencies.'})
        if len(deps) >= 8:
            recommendations.append({'type':'high_coupling','node':node_id,'dependency_count':len(deps)})
        central.append((node_id, len(deps)))

    central.sort(key=lambda x: x[1], reverse=True)

    return {
        'status':'ok',
        'summary': model.get('summary', {}),
        'recommendations': recommendations[:50],
        'central_components': [n for n,_ in central[:10]],
        'recommendation_count': len(recommendations)
    }

@router.get('/node/{node_id}')
def find_node(node_id:str):
    node=kernel.find_node(node_id)
    if not node:
        return {'status':'not_found','node_id':node_id}
    return {'status':'ok','node':node}

@router.get('/node/{node_id}/dependencies')
def node_dependencies(node_id:str):
    return {'status':'ok', **kernel.dependencies(node_id)}

@router.get('/node/{node_id}/dependents')
def node_dependents(node_id:str):
    return {'status':'ok', **kernel.dependents(node_id)}

@router.get('/node/{node_id}/impact')
def node_impact(node_id:str):
    return {'status':'ok','impact':kernel.impact(node_id)}

@router.get('/impact/{node_id}')
def impact_alias(node_id:str):
    return {'status':'ok','impact':kernel.impact(node_id)}

@router.post('/refresh')
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
