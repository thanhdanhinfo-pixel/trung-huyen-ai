# HANDOVER — Deployment Activation Bootstrap 

Date: 2026-06-26

## Completed in source

- Added Drive visibility tools in `mcp.py`:
  - `drive_list_children`
  - `drive_tree`
  - `drive_index`
- Updated `openapi-mcp-v3.json` to version `3.5.0`.
- Added safe redeploy endpoint source code:
  - `POST /deployment/redeploy`
  - `GET /deployment/capabilities` with `redeploy_endpoint` and config.
- Added deployment infrastructure:
  - `cloudbuild.yaml`
  - environment-driven `deploy_cloud_run.sh`
  - `system/deployment/DEPLOYMENT_ACTIVATION.md`
- Added GitHub Actions workaround:
  - `system/deployment/templates/deploy-cloud-run.workflow.yml`
  - `scripts/install_deploy_workflow.sh`
  - `scripts/activate_deploy_workflow.py`
  - `system/deployment/ACTIVATION_PACKET.md`
  - `system/deployment/RUNTIME_ACTIVATION_BLOCKER.md`

## Runtime status observed

Current Cloud Run runtime is still old:

```text
POST /deployment/redeploy -> 404 Not Found
GET /deployment/capabilities -> no redeploy_endpoint
GET /mcp/tools -> no drive_list_children / drive_tree / drive_index
```

## Blocker

A first external deployment is required. The current runtime cannot self-redeploy because it predates the redeploy endpoint.

GitHub workflow creation was blocked by:

```text
403 Forbidden on .github/workflows/deploy-cloud-run.yml
```

Cause: current GitHub token lacks `workflow` permission.

## Activation paths

Preferred:

```bash
export GITHUB_TOKEN_WITH_WORKFLOW=<pat_with_repo_and_workflow_scope>
export GITHUB_OWNER=thanhdanhinfo-pixel
export GITHUB_REPO=trung-huyen-ai
python scripts/activate_deploy_workflow.py
```

Then configure GitHub secrets:

```text
GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT_JSON
```

Alternative:

```bash
PROJECT_ID=<gcp-project> ./deploy_cloud_run.sh
```

## Next verification after activation

Run:

```text
GET /deployment/capabilities
GET /mcp/tools
POST /mcp/call drive_list_children
POST /mcp/call drive_tree
POST /mcp/call drive_index
```

Expected:

```text
redeploy_endpoint: true
drive_list_children present
drive_tree present
drive_index present
```

## Operating rule

Do not proceed to cleanup, rollback automation, or repository restructuring until runtime activation passes smoke tests.
