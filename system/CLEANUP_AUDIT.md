# TRUNG_HUYEN_AI_OS CLEANUP AUDIT

## Scope
Repository cleanup after OMEGA expansion. No source-of-truth YAML/identity files should be deleted automatically.

## Keep as source of truth
- SELF_STATE.yaml
- CAPABILITY_REGISTRY.yaml
- DIGITAL_TWIN.yaml
- SYSTEM_MODEL.yaml
- constitution.yaml
- CORE_BRAIN_INDEX.yaml
- ACADEMY_MODEL.yaml

## Candidate groups to consolidate

### Event system
Current files:
- event_bus.py
- event_stream.py
- event_ack.py
- event_ack_store.py
- event_retention.py
- event_subscriptions.py
- redis_event_bus.py
- distributed_routing.py
- distributed_backend.py
- ws_subscriptions.py

Action:
- Keep files for now.
- Add facade module: event_system.py.
- Route public imports through facade later.

### Scheduler / workers
Current files:
- scheduler_runtime.py
- production_scheduler.py
- runtime_bootstrap.py
- retention_worker.py
- evolution_worker.py
- worker_supervision.py

Action:
- Keep files for now.
- Add facade module: scheduler_system.py.

### Capability model
Current files:
- capability_evolution.py
- capability_lineage.py
- capability_dependencies.py
- capability_registry_v3.py
- dependency_risk.py

Action:
- Keep files for now.
- Add facade module: capability_system.py.

### Learning / evolution
Current files:
- reflection_engine.py
- learning_engine.py
- adaptation_engine.py
- evolution_engine.py
- evolution_history.py
- autonomous_governance.py
- knowledge_graph.py

Action:
- Keep files for now.
- Add facade module: evolution_system.py.

## Risk notes
- app.py is large and should not be rewritten wholesale.
- api/system_runtime.py is dense and should be split later.
- Several foundation files are small by design; deleting them may break imports.

## Cleanup status
- CLEANUP-1 audit: complete
- CLEANUP-2 facade consolidation: pending
- CLEANUP-3 API split: pending
- CLEANUP-4 validation repair: pending
