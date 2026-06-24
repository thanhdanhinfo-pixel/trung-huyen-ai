from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel, Field
from kernel.kernel import kernel
from kernel.observation.system_observer import system_observer
from services.repository_tree_loader import repository_tree_loader

router = APIRouter(prefix='/system-awareness', tags=['System Awareness'])

class RefreshSystemModelRequest(BaseModel):
    paths: List[str] | None = Field(default=None)
    files: List[Dict[str, Any]] | None = Field(default=None)


def _ensure_runtime_model_loaded() -> None:
    try:
        summary = kernel.system_model.summary()
        if summary.get('node_count', 0) > 20:
            return
        loaded = repository_tree_loader.load(['api', 'kernel', 'services'])
        if getattr(loaded, 'files', None):
            kernel.refresh_system_model(files=loaded.files)
    except Exception:
        pass

@router.get('/summary')
def system_awareness_summary():
    return {'status': 'ok','awareness': kernel.self_awareness(),'summary': kernel.system_summary(),'discovery': kernel.discovery_status()}

@router.get('/model')
def export_system_model():
    _ensure_runtime_model_loaded()
    return {'status': 'ok', 'system_model': kernel.export_system_model()}

@router.get('/observe')
def observe_system():
    return {'status': 'ok', 'observation': system_observer.observe(kernel)}

@router.get('/health')
def architecture_health():
    _ensure_runtime_model_loaded()
    report = kernel.system_model.architecture_report()
    return {'status': 'ok','health': report.get('health'),'risk_score': report.get('risk_score'),'summary': report.get('summary'),'cycle_count': report.get('cycle_count'),'orphan_count': report.get('orphan_count'),'high_risk_count': report.get('high_risk_count'),'critical_nodes': report.get('critical_nodes', [])[:5]}

@router.get('/cycles')
def architecture_cycles():
    cycles = kernel.system_model.detect_cycles()
    return {'status': 'ok', 'cycle_count': len(cycles), 'cycles': cycles}

@router.get('/criticality/{node_id}')
def node_criticality(node_id: str):
    return {'status': 'ok', 'criticality': kernel.system_model.criticality_score(node_id)}

@router.get('/mermaid')
def mermaid_graph():
    _ensure_runtime_model_loaded()
    return {'status': 'ok', 'mermaid': kernel.system_model.mermaid_graph()}

@router.get('/report')
def architecture_report():
    _ensure_runtime_model_loaded()
    return {'status': 'ok', 'report': kernel.system_model.architecture_report()}

@router.get('/recommendations')
def architecture_recommendations():
    _ensure_runtime_model_loaded()
    report = kernel.system_model.architecture_report()
    recommendations = []
    for node in report.get('orphans', [])[:50]:
        recommendations.append({'type': 'orphan_candidate', 'node': node})
    for item in report.get('critical_nodes', []):
        if item.get('level') in {'critical', 'high'}:
            recommendations.append({'type': 'high_criticality','node': item.get('node_id'),'score': item.get('score'),'level': item.get('level')})
    for cycle in report.get('cycles', []):
        recommendations.append({'type': 'circular_dependency', 'cycle': cycle})
    return {'status': 'ok','recommendations': recommendations[:50],'central_components': [item.get('node_id') for item in report.get('critical_nodes', [])[:10]],'recommendation_count': len(recommendations)}

@router.get('/graph')
def architecture_graph():
    _ensure_runtime_model_loaded()
    model = kernel.export_system_model()
    return {'status': 'ok','summary': model.get('summary', {}),'nodes': list(model.get('nodes', {}).values()),'edges': model.get('relationships', [])}

@router.get('/node/{node_id}')
def find_node(node_id: str):
    node = kernel.find_node(node_id)
    if not node:
        return {'status': 'not_found', 'node_id': node_id}
    return {'status': 'ok', 'node': node}

@router.get('/node/{node_id}/dependencies')
def node_dependencies(node_id: str):
    return {'status': 'ok', **kernel.dependencies(node_id)}

@router.get('/node/{node_id}/dependents')
def node_dependents(node_id: str):
    return {'status': 'ok', **kernel.dependents(node_id)}

@router.get('/node/{node_id}/impact')
def node_impact(node_id: str):
    return {'status': 'ok', 'impact': kernel.impact(node_id)}

@router.get('/impact/{node_id}')
def impact_alias(node_id: str):
    return {'status': 'ok', 'impact': kernel.impact(node_id)}

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
