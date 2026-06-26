from fastapi import APIRouter

from system import observability, system_awareness

router = APIRouter(prefix='/system', tags=['system-runtime'])


@router.get('/health')
def system_health():
    return observability.system_snapshot()


@router.get('/snapshot')
def system_snapshot():
    return observability.system_snapshot()


@router.get('/awareness')
def awareness():
    return system_awareness.snapshot()


@router.get('/capabilities')
def capabilities():
    return observability.capability_status()


@router.get('/governance')
def governance_report():
    return governance.health_report()


@router.get('/governance/actions')
def governance_actions():
    return {'actions': governance.recommended_actions()}

@router.get('/self-healing')
def healing_status():
    return self_healing.detect()

@router.post('/self-healing/repair')
def healing_repair():
    return self_healing.auto_repair()
