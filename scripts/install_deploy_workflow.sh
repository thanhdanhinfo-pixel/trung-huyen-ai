#!/bin/bash
set -euo pipefail 

SRC="system/deployment/templates/deploy-cloud-run.workflow.yml"
DST=".github/workflows/deploy-cloud-run.yml"

mkdir -p .github/workflows
cp "$SRC" "$DST"

echo "Installed $DST"
echo "Next steps:"
echo "1. git add $DST"
echo "2. git commit -m 'Activate Cloud Run deploy workflow'"
echo "3. git push origin main"
echo "4. Configure GitHub secrets: GCP_PROJECT_ID, GCP_SERVICE_ACCOUNT_JSON"
