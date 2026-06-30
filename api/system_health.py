from fastapi import APIRouter
from system import observability, system_awareness 

router=APIRouter(prefix='/system',tags=['system-health'])
@router.get('/health')
def health(): return observability.system_snapshot()
@router.get('/snapshot')
def snapshot(): return observability.system_snapshot()
@router.get('/awareness')
def awareness(): return system_awareness.snapshot()
@router.get('/capabilities')
def capabilities(): return observability.capability_status()
