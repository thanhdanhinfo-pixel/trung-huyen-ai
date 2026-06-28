# Deployment Activation
 
Status: deployment activation artifacts added.

## Required one-time activation

Set one of these runtime paths:

### Option A: Manual deploy

```bash
PROJECT_ID=<your-gcp-project> ./deploy_cloud_run.sh
```

### Option B: Cloud Build trigger

Use `cloudbuild.yaml` as the trigger config.

Trigger target:

```text
main branch -> cloudbuild.yaml -> Cloud Run service trung-huyen-ai
```

### Option C: Runtime redeploy endpoint

After the new image is live, configure one of:

```text
CLOUD_BUILD_TRIGGER_URL
REDEPLOY_COMMAND
```

Then call:

```json
{
  "approved": true,
  "reason": "activate latest TRUNG_HUYEN_AI_OS runtime"
}
```

against:

```text
POST /deployment/redeploy
```

## Post-deploy smoke tests

```text
GET /deployment/capabilities
GET /mcp/tools
POST /mcp/call drive_list_children
POST /mcp/call drive_tree
POST /mcp/call drive_index
```

Expected tools:

```text
drive_list_children
drive_tree
drive_index
```
