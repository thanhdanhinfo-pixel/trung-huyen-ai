# TRUNG_HUYEN_AI_OS — GPT ACTION SCOPE POLICY v1.0 

## Purpose

TRUNG_HUYEN_AI_OS is the master GPT Action for building, operating and governing the AI Operating System.

This GPT Action is not an Academy, CRM, marketing, coaching or project-delivery assistant.

## Allowed Scope

TRUNG_HUYEN_AI_OS may use actions for:

- Startup Bootstrap
- System state
- Runtime health
- Tool health
- GitHub read/write with Founder approval
- MCP gateway
- Repository observability
- Import scan
- Orphan module detection
- Refactor planning
- Capability Registry
- Self Awareness
- Workers and scheduler
- Governance and protected-file policy

## Excluded Scope

Do not add actions for these domains into TRUNG_HUYEN_AI_OS:

- Academy training operations
- Student coaching
- CRM
- Marketing content
- Sales operations
- Customer project delivery
- Dự án thực chiến

Those domains must use separate GPTs and separate action schemas.

## Startup Group

The required startup action is:

```http
GET /system/khoi-dong
```

This endpoint is the Startup Truth for all GPT Action conversations.

## Action Quota Rule

Keep the TRUNG_HUYEN_AI_OS action set focused and below GPT Action operation limits.

Preferred action groups:

- `/system/khoi-dong`
- `/system/tool-health`
- `/github/read`
- `/github/update`
- `/github/list`
- `/github/runtime/status`
- `/mcp/call`
- `/repo/status`
- `/repo/analyze`
- `/system/import-scan`
- `/system/orphan-modules`
- `/system/refactor-plan`

Do not expose the full dynamic OpenAPI to this GPT if it exceeds action limits.
