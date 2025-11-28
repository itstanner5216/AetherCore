#!/bin/bash
# AetherCore Gateway - Koyeb Deployment Script
# Deploys the service using Koyeb CLI
#
# USAGE:
# 1. Copy this file to koyeb_deploy.sh
# 2. Replace all placeholder values with your actual API keys
# 3. Run: chmod +x koyeb_deploy.sh && ./koyeb_deploy.sh

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
export KOYEB_TOKEN="${KOYEB_API_KEY:-YOUR_KOYEB_API_KEY_HERE}"

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
  --env SKILLS_CONFIG_PATH=../skills_config.json \
  --env API_KEY=YOUR_API_KEY_HERE \
  --env GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE \
  --env GOOGLE_CSE_ID=YOUR_GOOGLE_CSE_ID_HERE \
  --env BRAVE_API=YOUR_BRAVE_API_KEY_HERE \
  --env SERPER_API_KEY=YOUR_SERPER_API_KEY_HERE \
  --env WEBSCRAPING_API_KEY=YOUR_WEBSCRAPING_API_KEY_HERE \
  --env SCRAPINGANT_API_KEY=YOUR_SCRAPINGANT_API_KEY_HERE \
  --checks 8000:http:/health \
  --skip-cache

echo ""
echo "Deployment initiated!"
echo ""
echo "Monitor deployment: koyeb service logs aethercore-gateway -f"
echo "Get service info: koyeb service get aethercore-gateway"
echo ""
