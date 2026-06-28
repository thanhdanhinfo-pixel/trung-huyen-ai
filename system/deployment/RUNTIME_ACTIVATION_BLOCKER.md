# Runtime Activation Blocker

## Current blocker 

The repository token available to TRUNG_HUYEN_AI_OS can write normal repository files, but GitHub returned `403 Forbidden` for:

```text
.github/workflows/deploy-cloud-run.yml
```

This means the token lacks the GitHub `workflow` permission. 

## Workaround added

A workflow template has been added at:

```text
system/deployment/templates/deploy-cloud-run.workflow.yml
```

A local installer has been added at:

```text
scripts/install_deploy_workflow.sh
```

## Activation steps

Run locally with a GitHub identity that has workflow permission:

```bash
bash scripts/install_deploy_workflow.sh
git add .github/workflows/deploy-cloud-run.yml
git commit -m "Activate Cloud Run deploy workflow"
git push origin main
```

Then configure GitHub repository secrets:

```text
GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT_JSON
```

## After activation

The workflow can deploy the latest source to Cloud Run. After one successful deploy, these endpoints should become available in runtime:

```text
POST /deployment/redeploy
GET /deployment/capabilities -> redeploy_endpoint: true
POST /mcp/call -> drive_list_children / drive_tree / drive_index
```

## Why this exists

The current Cloud Run image is old and cannot expose the new `/deployment/redeploy` endpoint until one external deploy occurs. This file documents the bootstrap bridge.
