#!/bin/bash
# Deploy TamilNadai Workbench v2 to Cloud Run
# Usage: bash deploy.sh

set -e

# Configuration
PROJECT_ID="gen-lang-client-0871147736"  # HalaTuju GCP project
SERVICE_NAME="tamilnadai"
REGION="asia-southeast1"

echo "=== Deploying TamilNadai Workbench v2 ==="
echo "GCP Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Build and deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --no-cpu-throttling \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars "DEBUG=False" \
  --set-env-vars "DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')" \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --set-env-vars "DATABASE_URL=${DATABASE_URL}"

echo ""
echo "=== Deployment complete ==="
echo "Get the URL with: gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)'"
echo ""
echo "IMPORTANT: After deploying, update ALLOWED_HOSTS:"
echo "  gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars ALLOWED_HOSTS=<your-service-url>"
