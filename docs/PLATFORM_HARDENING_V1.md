# Platform Hardening V1

## Implemented in Repository
- Router Registry V2
- Governance V1
- Startup metrics
- Health/readiness/liveness
- Payload limits
- Soft rate limiting
- Docs protection

## External Actions Required

### Cloud Armor
Status: PENDING INFRASTRUCTURE
Reason: Requires GCP project-level configuration.

Recommended rules:
- Global rate limits for /chat and /rag/*
- Geo/IP filtering if required
- WAF managed protections

### Redis Distributed Rate Limiting
Status: PENDING INFRASTRUCTURE
Reason: Requires shared state outside Cloud Run instances.

Target design:
Client -> Cloud Armor -> Cloud Run -> Redis counters -> FastAPI

### GPT Federation
Required startup endpoints:
- /system/khoi-dong
- /system/boot-v3
- /system/active-task
- /system/global-memory
- /system/next-actions

Validation checklist:
- active_task present in startup payloads
- OpenAPI schema exposes required endpoints
- Brain/Academy/Worker GPTs consume the same startup contract
