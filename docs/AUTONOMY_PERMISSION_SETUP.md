# TRUNG_HUYEN_AI_OS Autonomy Permission Setup

This document lists the external permissions required for TRUNG_HUYEN_AI_OS to observe and recover its own runtime.

## Current limitation

The AI can update repository files through MCP, but it cannot self-grant Google Cloud IAM, read Cloud Run logs directly, rollback Cloud Run revisions, or inspect GitHub Checks unless those capabilities are explicitly exposed.

## Phase 1: read-only observability

Grant read-only access first:

- Cloud Run service/revision read access
- Cloud Logging read access
- Cloud Build read access
- GitHub Checks/status read access

Expected outcome:

- The AI can diagnose Cloud Build and Cloud Run failures without the Founder copying logs manually.

## Phase 2: safe test execution

Expose a restricted MCP tool for safe tests only:

```bash
python -c "import app; print('APP_IMPORT_OK')"
python -m compileall .
```

Rules:

- No arbitrary shell by default.
- No secret printing.
- No write operations.

## Phase 3: controlled recovery

Expose approved recovery tools:

- List Cloud Run revisions
- Identify latest green revision
- Propose rollback
- Execute rollback only after Founder approval

## Phase 4: restricted command execution

Only after the system is stable, add a whitelist-based command runner.

Default state must remain disabled.

## Required MCP tools to add later

```text
cloud_run_logs_read
cloud_run_revisions_list
cloud_run_rollback_approved
cloud_build_status_read
github_checks_read
safe_import_test
import_graph_scan
```

## Protected rule

No tool that can mutate Cloud Run traffic, trigger builds, or execute shell commands may run without explicit Founder approval.
