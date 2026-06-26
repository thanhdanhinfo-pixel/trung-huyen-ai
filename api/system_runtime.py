from fastapi import APIRouter

from system import observability, system_awareness, governance

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
