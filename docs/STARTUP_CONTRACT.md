# TRUNG_HUYEN_AI_OS — STARTUP CONTRACT v1.0

## Trigger Commands

When Founder sends exactly one of:

- `Khởi động`
- `START`
- `THOS START`

TRUNG_HUYEN_AI_OS must call:

```http
GET /system/khoi-dong
```

## Required Payload

The startup endpoint must return or aggregate:

- `self_state`
- `capability_registry`
- `checkpoint`
- `global_memory`
- `last_actions`
- `next_actions`
- `runtime`
- `verified_metrics`
- `tool_health`
- `active_endpoints`
- `gpt_network_policy`

## Required Behavior

After loading startup payload:

1. Prioritize system data over conversation memory.
2. Continue from `next_actions`.
3. Do not ask Founder to repeat previous history.
4. Do not infer when system data exists.
5. If `/system/khoi-dong` fails, try `/system/boot-v3`.
6. If both fail, report runtime startup failure briefly.

## Source of Truth Priority

1. `/system/khoi-dong`
2. Self State
3. Capability Registry
4. System Awareness
5. Runtime State
6. System Model
7. Repository State
8. Google Drive
9. Conversation Memory
10. Inference

## Production Endpoint

Current canonical startup endpoint:

```http
GET /system/khoi-dong
```

Compatibility endpoint:

```http
GET /system/boot-v3
```
