# Repository Health Report — 2026-07-01

## Scope
This report was generated after Founder approval for phased cleanup: A → C → B.

## Current Baseline
- Preflight: READY_TO_EXECUTE
- Tools: GitHub read/write, Drive, MCP, Runtime available
- Import scan: clean after fixing `system/capability/__init__.py`
- Known SyntaxError: resolved
- Orphan candidates: 146
- Policy: no delete, no mass move, no protected-file change without explicit approval

## Phase A Classification

### KEEP / Protected
- `mcp.py` — protected legacy/root MCP compatibility surface; keep until runtime trace confirms no external dependency.

### COMPATIBILITY_SHIM Candidates
Prioritize only after verification:
- `health.py`
- `orchestrator.py`
- `scheduler.py`

Defer:
- `chat.py` — contains `ChatRequest` model and must not be replaced blindly.
- `api/chat.py` — route/service behavior requires separate runtime verification.

### ACTIVE_UNREFERENCED — Manual Runtime Trace Required
- `document_cache.py`
- `long_term_memory.py`

### REVIEW_ORPHAN_CANDIDATE
Inspect before archive. Examples:
- `admin.py`
- `ai_ceo.py`
- `ai_governance.py`
- `answer_validator.py`
- `audit_log.py`
- `citation_engine.py`
- `context_builder.py`
- `conversation_memory.py`
- `logger.py`
- `master_planner.py`
- `metrics.py`
- `nightly_sync.py`
- `pdf_reader.py`
- `prompt.py`
- `prompt_manager.py`
- `quality_score.py`
- `reflection_engine.py`
- `research_agent.py`
- `security_layer.py`
- `self_improvement.py`
- `settings.py`
- `tool_registry.py`

### UNKNOWN_UNREFERENCED — Dependency Scan Required
Large groups requiring dependency and runtime checks:
- `api/*` unreferenced endpoints
- `bootstrap/*`
- `kernel/*` package boundaries
- `knowledge/*`
- `legacy/*`
- `services/*` auxiliary runtimes
- `system/*` facade and package modules
- `tools/*`
- `worker/__init__.py`

## Phase C Plan — Drive Tree Optimization
Implement a defensive payload limit for `/mcp/drive-tree` or the underlying Drive tree builder:
- default limit: 500 nodes
- response fields: `truncated`, `limit`, `returned_count`
- preserve existing behavior for smaller trees
- avoid loading full Drive tree in GPT action responses

## Phase B Plan — Compatibility Shims
Proceed only for files with clear target modules and no unique symbols:
- `orchestrator.py` → `agent_orchestrator.py`
- `scheduler.py` → `system.production_scheduler` or existing scheduler runtime after verification
- `health.py` → `api.health` only if API-compatible

## Safety Rules
- No delete during this phase.
- No archive/move during this phase.
- Preserve backward compatibility.
- Run import scan after each code change.

## Status
- Phase A: completed as classification report.
- Phase C: pending implementation.
- Phase B: pending verification after Phase C.
