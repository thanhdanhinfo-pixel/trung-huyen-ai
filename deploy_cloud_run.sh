#!/bin/bash
PROJECT_ID=YOUR_PROJECT
SERVICE=trung-huyen-ai
REGION=asia-southeast1

gcloud run deploy $SERVICE \
  --source . \
  --region $REGION \
  --allow-unauthenticated
