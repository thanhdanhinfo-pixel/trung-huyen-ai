#!/usr/bin/env bash
set -euo pipefail

# Example only. Replace placeholders before running.
# Do not commit real secrets into the repository.

PROJECT_ID="YOUR_PROJECT_ID"
REGION="asia-southeast1"
SERVICE_NAME="trung-huyen-ai"
AI_RUNTIME_SERVICE_ACCOUNT="YOUR_AI_RUNTIME_SERVICE_ACCOUNT_EMAIL"

# Read-only observability permissions.
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${AI_RUNTIME_SERVICE_ACCOUNT}" \
  --role="roles/logging.viewer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${AI_RUNTIME_SERVICE_ACCOUNT}" \
  --role="roles/run.viewer"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${AI_RUNTIME_SERVICE_ACCOUNT}" \
  --role="roles/cloudbuild.builds.viewer"

# Optional later, only if approved recovery is required.
# gcloud projects add-iam-policy-binding "$PROJECT_ID" \
#   --member="serviceAccount:${AI_RUNTIME_SERVICE_ACCOUNT}" \
#   --role="roles/run.developer"

cat <<EOF
Permission setup example complete.
Next required step: expose MCP tools that call Cloud Logging, Cloud Run revision read, and Cloud Build status read.
EOF
