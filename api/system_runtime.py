from fastapi import APIRouter
from system import observability, system_awareness, governance, self_healing, policy_engine, rule_engine, event_bus, evolution_engine

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
@router.get('/events/retention')
def event_retention_policy():
    from system.event_retention import event_retention
    return event_retention.policy()

@router.get('/events/subscriptions')
def event_subs():
    from system.event_subscriptions import event_subscriptions
    return event_subscriptions.snapshot()

@router.get('/events/live')
def events_live(limit:int=20): return {'mode':'polling-v1','events':event_bus.recent(limit)}
@router.get('/evolution')
def evolution(): return evolution_engine.evolve()
