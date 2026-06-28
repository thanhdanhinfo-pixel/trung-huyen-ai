# GitHub Actions Deploy

This repository now contains:
 
```text
.github/workflows/deploy-cloud-run.yml
```

## Purpose

This solves the bootstrap problem where the old Cloud Run image cannot expose the new `/deployment/redeploy` endpoint until one external deployment occurs.

## Required GitHub secrets

Configure these repository secrets:

```text
GCP_PROJECT_ID
GCP_SERVICE_ACCOUNT_JSON
```

The service account should have permissions sufficient for Cloud Run source deploy, typically:

```text
Cloud Run Admin
Cloud Build Editor
Artifact Registry Writer
Service Account User
```

## How to activate

Option A: Push to `main` affecting deploy paths.

Option B: Open GitHub Actions and manually run:

```text
Deploy to Cloud Run
```

## After successful deploy

Run smoke tests:

```text
GET /deployment/capabilities
GET /mcp/tools
POST /mcp/call { tool: drive_list_children }
POST /mcp/call { tool: drive_tree }
POST /mcp/call { tool: drive_index }
```

Expected new runtime capabilities:

```text
redeploy_endpoint: true
drive_list_children
drive_tree
drive_index
```
