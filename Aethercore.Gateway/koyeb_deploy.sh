#!/bin/bash
# AetherCore Gateway - Koyeb Deployment Script
# Deploys the service using Koyeb CLI

set -e

echo "=========================================="
echo "AetherCore Gateway - Koyeb Deployment"
echo "=========================================="

# Check if koyeb CLI is installed
if ! command -v koyeb &> /dev/null; then
    echo "Koyeb CLI not found. Installing..."

    # Install Koyeb CLI
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://app.koyeb.com/install.sh | bash
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install koyeb/tap/koyeb-cli
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "On Windows, download from: https://github.com/koyeb/koyeb-cli/releases"
        echo "Or use: scoop install koyeb-cli"
        exit 1
    fi
fi

# Set API token from environment
export KOYEB_TOKEN="${KOYEB_API_KEY:-5ue0i50v18viyfdrjgm7rea3x7xnjeqe3h57z0idxh7o62vdq9oiyux5y7b5kfjf}"

echo ""
echo "Creating/Updating AetherCore Gateway service..."
echo ""

# Deploy using koyeb CLI
koyeb service create aethercore-gateway \
  --app aethercore \
  --git github.com/itstanner5216/AetherCore \
  --git-branch main \
  --git-builder docker \
  --docker-dockerfile Dockerfile \
  --ports 8000:http \
  --routes /:8000 \
  --instance-type nano \
  --region was \
  --env ENVIRONMENT=production \
  --env DEBUG=false \
  --env PORT=8000 \
  --env HOST=0.0.0.0 \
  --env LOG_LEVEL=INFO \
  --env CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com \
  --env RATE_LIMIT_REQUESTS=100 \
  --env RATE_LIMIT_WINDOW=3600 \
  --env SKILLS_CONFIG_PATH=skills_config.json \
  --env API_KEY=f3a0c4b7e1d9c0f247a6df81b2439e57c1d84e3ab9a92f7db08f6c2cd41e5af0 \
  --env GOOGLE_API_KEY=AIzaSyDLSW6qz4tC9Aq0p2yO0gbmrrIBeKjGdBs \
  --env GOOGLE_CSE_ID=739bdcbb2b51b4409 \
  --env BRAVE_API=BSAUZcHnbsKgi9GTsu4wQV2SPEeZ3wy \
  --env SERPER_API_KEY=8b0733a1da1ace1e16a34f5a396b48e4daa4d88e \
  --env WEBSCRAPING_API_KEY=DXXGG7k1XgDQI1EPvq2ZCobU3N1uksPo \
  --env SCRAPINGANT_API_KEY=0f53dcf52bc3454687ff777304dbd583 \
  --checks 8000:http:/health \
  --skip-cache

echo ""
echo "Deployment initiated!"
echo ""
echo "Monitor deployment: koyeb service logs aethercore-gateway -f"
echo "Get service info: koyeb service get aethercore-gateway"
echo ""
