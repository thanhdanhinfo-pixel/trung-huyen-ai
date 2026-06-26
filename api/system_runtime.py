import asyncio
import json
from fastapi import APIRouter, WebSocket
from fastapi.responses import StreamingResponse
from system import observability, system_awareness, governance, self_healing, policy_engine, rule_engine, event_bus, evolution_engine
from system.event_ack import event_ack
from system.distributed_routing import distributed_routing
from system.scheduler_runtime import scheduler_runtime
from system.worker_supervision import worker_supervision
from system.event_retention import event_retention
from system.event_subscriptions import event_subscriptions

router=APIRouter(prefix='/system',tags=['system-runtime'])
@router.get('/health')
def health(): return observability.system_snapshot()
@router.get('/snapshot')
def snapshot(): return observability.system_snapshot()
@router.get('/awareness')
def awareness(): return system_awareness.snapshot()
@router.get('/capabilities')
def capabilities(): return observability.capability_status()
@router.get('/governance')
def gov(): return governance.health_report()
@router.get('/governance/actions')
def gov_actions(): return {'actions':governance.recommended_actions()}
@router.get('/policies')
def policies(): return policy_engine.evaluate()
@router.get('/policies/rollback')
def rollback(): return policy_engine.rollback_policy()
@router.get('/rules')
def rules(): return rule_engine.evaluate()
@router.post('/rules/execute')
def rules_exec(): return rule_engine.execute()
@router.get('/self-healing')
def sh(): return self_healing.detect()
@router.post('/self-healing/repair')
def sh_repair(): return self_healing.auto_repair()
@router.get('/planner')
def planner(): return observability.planner_status()
@router.get('/workers')
def workers(): return observability.worker_status()
@router.get('/tasks')
def tasks(): return observability.task_status()
@router.get('/events')
def events(limit:int=50): return event_bus.recent(limit)
@router.get('/events/stats')
def event_stats(): return event_bus.stats()
@router.get('/events/live')
def events_live(limit:int=20): return {'mode':'polling-v1','events':event_bus.recent(limit)}
@router.get('/events/retention')
def event_retention_policy(): return event_retention.policy()
@router.get('/events/retention/cleanup')
def event_cleanup(): return event_retention.cleanup_status()
@router.get('/events/subscriptions')
def event_subs(): return event_subscriptions.snapshot()
@router.post('/events/ack')
def ack(event_id:str, consumer:str): return event_ack.acknowledge(event_id, consumer)
@router.get('/events/acks')
def acks(): return event_ack.snapshot()
@router.get('/events/route')
def route(event_type:str): return distributed_routing.route(event_type)

async def _sse_generator(limit:int=20):
    while True:
        payload=json.dumps({'events': event_bus.recent(limit)}, ensure_ascii=False)
        yield f'data: {payload}\n\n'
        await asyncio.sleep(2)

@router.get('/events/sse')
def events_sse(limit:int=20):
    return StreamingResponse(_sse_generator(limit), media_type='text/event-stream')

@router.websocket('/events/ws')
async def events_ws(websocket: WebSocket):
    from system.ws_subscriptions import ws_subscriptions
    await websocket.accept()
    subs=['*']
    try:
        first=await websocket.receive_json()
        subs=first.get('subscribe',['*'])
    except Exception:
        pass
    try:
        while True:
            events=event_bus.recent(20)
            filtered=[]
            for e in events:
                et=e.get('type','') if isinstance(e,dict) else ''
                if subs==['*'] or ws_subscriptions.match(subs,et):
                    filtered.append(e)
            await websocket.send_json({'events': filtered})
            await asyncio.sleep(2)
    except Exception:
        await websocket.close()

@router.get('/scheduler')
def scheduler_status(): return scheduler_runtime.status()
@router.post('/scheduler/run')
def scheduler_run(): return scheduler_runtime.run_cycle()
@router.get('/supervision')
def supervision(): return worker_supervision.inspect()
@router.post('/supervision/restart')
def restart_worker(worker_name:str): return worker_supervision.restart(worker_name)
@router.get('/evolution')
def evolution(): return evolution_engine.evolve()
