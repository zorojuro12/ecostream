#!/usr/bin/env bash
# Deploy the AI Forecasting Service to AWS Lambda via SAM CLI.
# Prerequisites: AWS CLI configured, SAM CLI installed, Docker running.
#
# Usage:
#   cd services/ai-forecasting-python
#   ./scripts/deploy-lambda.sh                     # guided (confirms changeset)
#   ./scripts/deploy-lambda.sh --no-confirm-changeset  # non-interactive
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SERVICE_DIR"

echo "=== Building SAM application (Docker image) ==="
sam build

echo ""
echo "=== Deploying to AWS ==="
sam deploy "$@"

echo ""
echo "=== Deployment complete ==="
sam list stack-outputs --stack-name ecostream-ai-forecasting --output table 2>/dev/null || true
