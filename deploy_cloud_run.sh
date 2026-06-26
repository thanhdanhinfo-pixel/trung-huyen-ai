#!/bin/bash
set -euo pipefail

PROJECT_ID=${PROJECT_ID:-${GOOGLE_CLOUD_PROJECT:-}}
SERVICE=${SERVICE:-trung-huyen-ai}
REGION=${REGION:-asia-southeast1}

if [ -z "$PROJECT_ID" ]; then
  echo "Missing PROJECT_ID. Set PROJECT_ID or GOOGLE_CLOUD_PROJECT."
  exit 1
fi

echo "Deploying $SERVICE to project=$PROJECT_ID region=$REGION"

gcloud config set project "$PROJECT_ID"
gcloud run deploy "$SERVICE" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated
