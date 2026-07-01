# THOS_PARALLEL_COLLABORATION_PROTOCOL_V1

## Purpose
Allow multiple AI sessions or GPT workers to operate on the same TRUNG_HUYEN_AI_OS ecosystem without overwriting each other, duplicating work, or crossing ownership boundaries.

## Mandatory Mode
```text
PARALLEL_MODE=ON
SHARED_SYSTEM=TRUE
NO_OVERRIDE_WITHOUT_APPROVAL=TRUE
RESPECT_OWNERSHIP_BOUNDARIES=TRUE
SOURCE_OF_TRUTH=GITHUB_MAIN_AND_SYSTEM_MEMORY
```

## Authority
Founder has final authority.
TRUNG_HUYEN_AI_OS is the central coordinator.
No worker AI may override Founder decisions or system governance.

## Source of Truth Priority
1. `/system/khoi-dong`
2. GitHub `main`
3. `system/GLOBAL_PROTOCOLS/*`
4. `system/TASK_REGISTRY.yaml`
5. Repository Health Reports
6. Google Drive / Global Memory
7. Current conversation
8. Inference

## Role Boundaries

### RUNTIME_AI
Owns:
- Backend code
- API endpoints
- Cloud Run runtime
- Deployments
- `drive.py`
- `api/mcp.py`
- Security and governance code
- Observability and tool health

May perform after Founder approval:
- Build
- Deploy
- Runtime patch
- System endpoint update

Must not do without explicit approval:
- Delete files
- Mass move files
- Change secrets
- Rewrite Drive content structure

### DRIVE_AI
Owns:
- Google Drive content
- Program knowledge
- Academy materials
- Knowledge maps
- RAG-ready content
- Parser/content extraction logic proposals
- Documentation and taxonomy

May perform after Founder approval:
- Create knowledge documents
- Propose parser/schema changes
- Organize program understanding

Must not do without explicit approval:
- Deploy runtime
- Change production backend
- Modify secrets
- Rewrite core runtime files directly

### SHARED FILES / SHARED AREAS
The following require explicit coordination before edit:
- `drive.py`
- `api/mcp.py`
- `app.py`
- `config.py`
- `services/action_registry.py`
- `system/security/*`
- `system/TASK_REGISTRY.yaml`
- startup endpoints
- deployment scripts

## Conflict Rules
If a session needs to change a file owned by another role:
1. Do not edit directly.
2. Create a PROPOSAL.
3. Include target files, reason, risks, rollback plan.
4. Wait for Founder or TRUNG_HUYEN_AI_OS coordinator decision.

If two sessions are working in parallel:
- Only one session may deploy at a time.
- Every code-changing session must report commit SHA.
- Every runtime-changing session must report build/deploy ID.
- Every Drive-changing session must report document path and purpose.

## Required Work Log After Changes
Each AI session must output:
```yaml
work_log:
  role: RUNTIME_AI | DRIVE_AI | OTHER
  files_changed: []
  drive_docs_changed: []
  commit_sha: null
  build_id: null
  deploy_revision: null
  risks: []
  next_actions: []
```

## Protected Actions
Always require explicit Founder approval:
- Delete file
- Move many files
- Archive repository modules
- Deploy production
- Change secrets
- Change security policy
- Change task registry ownership
- Modify startup contract

## Startup Requirement
Any AI session working on TRUNG_HUYEN_AI_OS must load this protocol at startup or before making code/runtime/Drive changes.

Required startup marker:
```text
LOAD_PROTOCOL: THOS_PARALLEL_COLLABORATION_PROTOCOL_V1
```

## Final Principle
Many AI sessions may work together, but there must be one source of truth, one governance layer, one deployment authority at a time, and Founder remains the final decision maker.
