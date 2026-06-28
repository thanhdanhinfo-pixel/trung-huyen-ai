# Runtime Activation Packet

This packet exists because TRUNG_HUYEN_AI_OS has finished source-level deployment work, but the current Cloud Run image is old and cannot expose new runtime endpoints until one external activation occurs.

## Current blocker 

```text
POST /deployment/redeploy -> 404
GET /deployment/capabilities -> old schema
GitHub write to .github/workflows/* -> 403 Forbidden
```

Root cause:

```text
Current GitHub token lacks workflow permission.
Current Cloud Run image predates /deployment/redeploy.
```

## Activation Option A — GitHub API script

Use a GitHub PAT with `repo` + `workflow` scopes.

```bash
export GITHUB_TOKEN_WITH_WORKFLOW=<pat_with_workflow_scope>
export GITHUB_OWNER=thanhdanhinfo-pixel
export GITHUB_REPO=trung-huyen-ai
export GITHUB_BRANCH=main
python scripts/activate_deploy_workflow.py
```

Then configure GitHub secrets:

```text
GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT_JSON
```

Run GitHub Actions workflow:

```text
Deploy to Cloud Run
```

## Activation Option B — Local git copy

```bash
bash scripts/install_deploy_workflow.sh
git add .github/workflows/deploy-cloud-run.yml
git commit -m "Activate Cloud Run deploy workflow"
git push origin main
```

## Activation Option C — Manual Cloud Run deploy

```bash
PROJECT_ID=<gcp-project> ./deploy_cloud_run.sh
```

## After activation smoke tests

```text
GET /deployment/capabilities
GET /mcp/tools
POST /mcp/call {"tool":"drive_list_children","arguments":{"limit":10}}
POST /mcp/call {"tool":"drive_tree","arguments":{"depth":2,"limit":50}}
POST /mcp/call {"tool":"drive_index","arguments":{"limit":100}}
```

Expected:

```text
redeploy_endpoint: true
drive_list_children
drive_tree
drive_index
```

## Completion condition

The system is considered runtime-activated when:

```text
/deployment/capabilities shows redeploy_endpoint=true
/mcp/tools includes drive_list_children, drive_tree, drive_index
```
