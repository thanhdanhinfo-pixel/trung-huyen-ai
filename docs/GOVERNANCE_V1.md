# Governance V1

## Purpose
Establish protected-file governance, approval requirements, and production safety rules for TRUNG_HUYEN_AI_OS.

## Protected Files

These files are production-sensitive and must not be overwritten, deleted, or mass-refactored without explicit Founder approval:

- app.py
- api/bootstrap_app.py
- api/router_registry.py
- api/app_middleware.py
- config.py
- services/health_service.py
- api/routes/system_core.py
- api/routes/actions.py

## Change Rules

### Rule 1: Observe First
Before modifying protected files:
1. Read current file state.
2. Identify exact target block.
3. Prefer small patches over full overwrites.
4. Avoid broad refactors unless approved.

### Rule 2: No Blind Overwrite
Do not use full-file replacement on protected files unless:
- The file is corrupted, or
- Founder explicitly approves full replacement, or
- A rollback path is known.

### Rule 3: Production Safety
Any change touching startup, middleware, security, routing, or health must include at least one of:
- smoke-test plan,
- rollback note,
- endpoint verification target.

### Rule 4: Security Boundary Protection
Changes to these areas require explicit review:
- authentication and authorization,
- rate limiting,
- payload limits,
- docs exposure,
- MCP/admin/runtime routers,
- action registry / tool registry.

### Rule 5: Runtime Isolation
Optional and experimental modules must not break core production routes.
Core routes include:
- /
- /health
- /livez
- /readiness
- /chat
- /drive/*
- /rag/*
- /actions.json

### Rule 6: Founder Approval Required
Founder approval is required before:
- deleting files,
- moving files in bulk,
- changing secrets,
- changing Cloud Run/runtime configuration,
- changing protected files by full overwrite,
- modifying governance policy.

## Smoke Test Targets

Minimum production smoke targets:

- GET /livez
- GET /readiness
- GET /health
- GET /actions.json
- POST /chat
- GET /drive/files
- GET /rag/search
- GET /system/startup-metrics

## Current Governance Status

- Protected files registry: ACTIVE
- Startup protection: ACTIVE
- Request correlation: ACTIVE
- Payload limits: ACTIVE
- Soft rate limiting: ACTIVE
- Docs production protection: ACTIVE
- Health/readiness/liveness: ACTIVE

## Known Limitations

- Soft rate limiting is per-instance only.
- Strict production rate limiting requires Cloud Armor or Redis-backed counters.
- GPT network synchronization requires external GPT Action configuration.

## Next Actions

1. Add repository-level protected files manifest.
2. Add Router Registry V2.
3. Add CI smoke-test checklist.
4. Add distributed rate limiting plan.
