# TRUNG_HUYEN_AI_OS — GPT NETWORK POLICY v1.0

## Architecture Principle

GPTs do not talk directly to each other.

All GPTs connect to the same backend and use shared system state.

```text
GPTs
  ↓
Shared Cloud Run Backend
  ↓
GitHub + Google Drive + Runtime + Memory
```

## Master GPT

`TRUNG_HUYEN_AI_OS` is the master GPT Action.

Responsibilities:

- Build and operate the AI Operating System
- Manage GitHub and runtime operations
- Manage startup state
- Manage observability and repository intelligence
- Coordinate but not replace specialized GPTs

## Specialized GPTs

### BỘ NÃO GỐC NGUYỄN DUY TRUNG

Scope:

- Founder philosophy
- Founder memory
- Thinking frameworks
- Principles and constitution

Actions:

- `/system/khoi-dong`
- Drive/RAG knowledge search

No GitHub write.

### TRUNG HUYỀN ACADEMY

Scope:

- Training
- Curriculum
- Students
- Coaching content
- Academy documents

Actions:

- `/system/khoi-dong`
- Drive/RAG
- document create/append when approved

No repository refactor actions.

### PROJECT GPT

Scope:

- Dự án thực chiến
- Client delivery
- Sprint planning
- Project documents

Actions:

- `/system/khoi-dong`
- Drive/project workspace actions

No core runtime refactor unless explicitly approved.

### WORKER GPT

Scope:

- Task execution
- Workflow execution
- Worker status

Actions:

- `/system/khoi-dong`
- worker/runtime/execute endpoints

## Shared Startup Rule

Every GPT in the ecosystem must support:

```text
Khởi động → GET /system/khoi-dong
```

The returned payload is the common state source.

## Immutable Rule

Do not merge Academy, Project, CRM or marketing actions into the master TRUNG_HUYEN_AI_OS action schema.
