# Dead Code Audit V1

## Scope
- app.py
- api/routes/*
- services/*
- api/router_registry.py
- api/app_middleware.py

## Objectives
1. Detect unused imports.
2. Detect legacy route handlers left after decomposition.
3. Detect routers not included in runtime.
4. Detect orphan modules.
5. Detect duplicated helper functions.

## Current Known Status

### Resolved by APP-DECOMPOSITION-V2
- Drive handlers migrated to api/routes/drive.py
- RAG handlers migrated to api/routes/rag.py and api/routes/rag_runtime.py
- Chat handler migrated to api/routes/chat.py
- Chat business logic migrated to services/chat_service.py
- System core handlers migrated to api/routes/system_core.py
- Actions schema migrated to api/routes/actions.py

### Resolved by Security & Reliability Hardening
- Request logging moved to api/app_middleware.py
- Request IDs implemented
- Payload limits implemented
- Soft rate limiting implemented
- Startup timeout implemented
- Health component model implemented
- Liveness/readiness endpoints implemented

## Findings

### LOW: app.py still owns root endpoint
Status: Accepted
Reason: Root endpoint serves static index fallback and is safe in composition root.

### LOW: app.py still owns optional router loading
Status: Accepted for now
Reason: Optional router loading is runtime-sensitive; move only after router registry V2.

### LOW: STARTUP_METRICS currently logged but not exposed
Status: Planned
Recommended action: expose via /system/startup-metrics or /readiness extension.

### MEDIUM: Soft rate limiting is per-instance only
Status: Known limitation
Recommended action: Cloud Armor or Redis-backed distributed limiter.

## No Critical Dead Code Found

Based on current decomposition state, no critical production dead-code risk is identified.

## Next Actions
1. Router Registry V2: centralize core router wiring.
2. Startup Metrics Exposure: expose metrics through safe internal endpoint.
3. Orphan Module Audit V1.
4. Protected File Governance V1.
