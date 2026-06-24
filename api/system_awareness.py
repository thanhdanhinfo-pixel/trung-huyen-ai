from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from kernel.kernel import kernel
from services.repository_tree_loader import repository_tree_loader

router = APIRouter(prefix='/system-awareness', tags=['System Awareness'])

class RefreshSystemModelRequest(BaseModel):
    paths: List[str] | None = Field(default=None)
    files: List[Dict[str, Any]] | None = Field(default=None)

@router.get('/summary')
def system_awareness_summary():
    return {'status':'ok','summary':kernel.system_summary(),'discovery':kernel.discovery_status()}

@router.get('/model')
def export_system_model():
    return {'status':'ok','system_model':kernel.export_system_model()}

@router.get('/health')
def architecture_health():
    model = kernel.export_system_model()
    nodes = model.get('nodes', {})
    cycles = []
    orphan_nodes = []
    max_depth = 0

    for node_id, node in nodes.items():
        deps = node.get('dependencies', [])
        if not deps:
            orphan_nodes.append(node_id)
        max_depth = max(max_depth, len(deps))
        for dep in deps:
            dep_node = nodes.get(dep, {})
            if node_id in dep_node.get('dependencies', []):
                cycles.append([node_id, dep])

    risk_score = len(cycles) * 10 + len(orphan_nodes)

    return {
        'status':'ok',
        'node_count': len(nodes),
        'orphan_nodes': orphan_nodes[:50],
        'orphan_count': len(orphan_nodes),
        'circular_dependencies': cycles,
        'circular_count': len(cycles),
        'max_dependency_depth': max_depth,
        'risk_score': risk_score,
        'health': 'good' if risk_score < 20 else 'warning' if risk_score < 50 else 'critical'
    }

@router.get('/recommendations')
def architecture_recommendations():
    model = kernel.export_system_model(); nodes=model.get('nodes',{})
    rec=[]; central=[]
    for nid,node in nodes.items():
        deps=node.get('dependencies',[])
        if not deps: rec.append({'type':'orphan_candidate','node':nid})
        if len(deps)>=8: rec.append({'type':'high_coupling','node':nid,'dependency_count':len(deps)})
        central.append((nid,len(deps)))
    central.sort(key=lambda x:x[1], reverse=True)
    return {'status':'ok','recommendations':rec[:50],'central_components':[n for n,_ in central[:10]]}

@router.get('/graph')
def architecture_graph():
    model=kernel.export_system_model()
    return {'status':'ok','summary':model.get('summary',{}),'nodes':list(model.get('nodes',{}).values()),'edges':model.get('relationships',[])}

@router.get('/impact/{node_id}')
def impact_alias(node_id:str):
    return {'status':'ok','impact':kernel.impact(node_id)}

@router.post('/refresh')
def refresh_system_model(req: RefreshSystemModelRequest):
    if req.files: return kernel.refresh_system_model(files=req.files)
    if req.paths:
        try:
            loaded=repository_tree_loader.load(req.paths)
            if loaded.files: return kernel.refresh_system_model(files=loaded.files)
        except Exception:
            pass
    return kernel.refresh_system_model(paths=req.paths, files=req.files)
