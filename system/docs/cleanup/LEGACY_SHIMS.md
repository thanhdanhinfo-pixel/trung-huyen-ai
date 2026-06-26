# Legacy Shims

Root `.py` files that remain are compatibility shims or public facades.

## Keep forever
- `system/__init__.py`
- source-of-truth YAML files
- identity/continuity documents until boot dependency audit is complete

## Active compatibility shims
- `event_bus.py`
- `event_ack.py`
- `event_ack_store.py`
- `event_retention.py`
- `event_subscriptions.py`
- `event_stream.py`
- `redis_event_bus.py`
- `distributed_backend.py`
- `distributed_routing.py`
- `ws_subscriptions.py`
- `bootstrap.py`
- `runtime_bootstrap.py`
- `agent_runtime.py`
- `task_runtime.py`
- `worker_supervision.py`
- `retention_worker.py`
- `evolution_worker.py`
- `rule_engine.py`
- `rule_engine_v2.py`
- `policy_engine.py`
- `knowledge_graph.py`
- `digital_twin.py`
- `digital_twin_simulation.py`
- `validation_report.py`
- `governance.py`
- `governance_audit.py`
- `autonomous_governance.py`
- `founder_control.py`
- `constitution.py`
- `system_awareness.py`
- `observability_layer.py`
- `self_healing.py`

## Removal policy
Do not delete active shims until import usage is audited across dashboard, API, workers, automation scripts, and mobile integrations.
