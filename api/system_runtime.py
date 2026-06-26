import asyncio
import json
from fastapi import APIRouter, WebSocket
from fastapi.responses import StreamingResponse

router = APIRouter(prefix='/system', tags=['system-runtime'])


def _safe(name, default=None):
    try:
        module = __import__(name, fromlist=['*'])
        return module
    except Exception as exc:
        print(f'SYSTEM_RUNTIME_IMPORT_FAILED {name}:', exc)
        return default


class _Stub:
    def __getattr__(self, _):
        return lambda *a, **k: {'status': 'disabled'}


observability = _safe('system.observability', _Stub())
system_awareness = _safe('system.system_awareness', _Stub())
governance = _safe('system.governance', _Stub())
event_bus = _safe('system.event_bus', _Stub())


@router.get('/health')
def health():
    if hasattr(observability, 'system_snapshot'):
        return observability.system_snapshot()
    return {'status': 'safe-mode'}


@router.get('/snapshot')
def snapshot():
    return health()


@router.get('/awareness')
def awareness():
    if hasattr(system_awareness, 'snapshot'):
        return system_awareness.snapshot()
    return {'status': 'safe-mode'}


@router.get('/events')
def events(limit: int = 20):
    if hasattr(event_bus, 'recent'):
        return event_bus.recent(limit)
    return []


async def _sse_generator():
    while True:
        yield 'data: {"status":"safe-mode"}\n\n'
        await asyncio.sleep(2)


@router.get('/events/sse')
def events_sse():
    return StreamingResponse(_sse_generator(), media_type='text/event-stream')


@router.websocket('/events/ws')
async def events_ws(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({'status': 'safe-mode'})
    await websocket.close()
