#!/usr/bin/env python3
"""
AetherCore Gateway - Koyeb Deployment Launcher
Simple, reliable deployment using Koyeb REST API

USAGE:
1. Copy this file to deploy.py
2. Replace all placeholder values with your actual API keys
3. Run: python deploy.py
"""

import os
import sys
import json
import time

# Check for requests library
try:
    import requests
except ImportError:
    print("Installing required package: requests")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Configuration
API_KEY = os.getenv("KOYEB_PERSONAL_ACCESS_TOKEN", "YOUR_KOYEB_PERSONAL_ACCESS_TOKEN_HERE").strip()
API_BASE = "https://app.koyeb.com/v1"
APP_NAME = "aethercore"
SERVICE_NAME = "aethercore-gateway"
GITHUB_REPO = "github.com/itstanner5216/AetherCore"

ENV_VARS = {
    "ENVIRONMENT": "production",
    "DEBUG": "false",
    "PORT": "8000",
    "HOST": "0.0.0.0",
    "LOG_LEVEL": "INFO",
    "CORS_ORIGINS": "https://chat.openai.com,https://chatgpt.com",
    "RATE_LIMIT_REQUESTS": "100",
    "RATE_LIMIT_WINDOW": "3600",
    "SKILLS_CONFIG_PATH": "../AetherCore.System/skills_config.json",
    "SEARCH_ENGINE_SERVER_URL": "http://localhost:3000",
    "API_KEY": "YOUR_API_KEY_HERE",
    "GATEWAY_API_KEY": "YOUR_API_KEY_HERE",
    "UPSTASH_REDIS_REST_URL": "YOUR_UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN": "YOUR_UPSTASH_REDIS_REST_TOKEN",
    "GOOGLE_API_KEY": "YOUR_GOOGLE_API_KEY_HERE",
    "GOOGLE_CSE_ID": "YOUR_GOOGLE_CSE_ID_HERE",
    "BRAVE_API": "YOUR_BRAVE_API_KEY_HERE",
    "SERPER_API_KEY": "YOUR_SERPER_API_KEY_HERE",
    "WEBSCRAPING_API_KEY": "YOUR_WEBSCRAPING_API_KEY_HERE",
    "SCRAPINGANT_API_KEY": "YOUR_SCRAPINGANT_API_KEY_HERE",
}


def api_call(method, endpoint, data=None):
    """Make Koyeb API call"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            resp = requests.request(method, url, headers=headers, json=data, timeout=30)

        return resp.status_code, resp.json() if resp.text else {}
    except Exception as e:
        return 500, {"error": str(e)}


def main():
    print("=" * 60)
    print("AetherCore Gateway - Koyeb Deployment")
    print("=" * 60)
    print()

    # Step 1: Check/create app
    print("[1/4] Checking app...")
    status, data = api_call("GET", "/apps")

    app_id = None
    if "apps" in data:
        for app in data["apps"]:
            if app["name"] == APP_NAME:
                app_id = app["id"]
                print(f"  [OK] App '{APP_NAME}' exists (ID: {app_id})")
                break

    if not app_id:
        print(f"  Creating app '{APP_NAME}'...")
        status, data = api_call("POST", "/apps", {"name": APP_NAME})
        if "app" in data:
            app_id = data["app"]["id"]
            print(f"  [OK] App created (ID: {app_id})")
        else:
            print(f"  [FAIL] Failed to create app: {data.get('message', 'Unknown error')}")
            sys.exit(1)

    # Step 2: Create service
    print()
    print("[2/4] Creating service...")

    service_payload = {
        "app_id": app_id,
        "definition": {
            "name": SERVICE_NAME,
            "type": "WEB",
            "regions": ["was"],
            "git": {
                "repository": GITHUB_REPO,
                "branch": "main"
            },
            "docker": {
                "dockerfile": "Aethercore.Gateway/Dockerfile"
            },
            "instance_types": [{"type": "nano"}],
            "ports": [
                {"port": 8000, "protocol": "http"},
                {"port": 3000, "protocol": "http"}
            ],
            "routes": [
                {"port": 8000, "path": "/aethercore"},
                {"port": 3000, "path": "/search"}
            ],
            "env": [{"key": k, "value": v} for k, v in ENV_VARS.items()],
            "health_checks": [{
                "http": {
                    "port": 8000,
                    "path": "/health"
                }
            }],
            "scalings": [{"min": 1, "max": 1}]
        }
    }

    status, data = api_call("POST", "/services", service_payload)

    if status == 409:
        print(f"  [INFO] Service '{SERVICE_NAME}' already exists")
        print("  Getting service info...")
        status, data = api_call("GET", f"/apps/{app_id}/services")
        if "services" in data:
            for svc in data["services"]:
                if svc["name"] == SERVICE_NAME:
                    service_id = svc["id"]
                    print(f"  [OK] Service ID: {service_id}")
                    break
    elif "service" in data:
        service_id = data["service"]["id"]
        print(f"  [OK] Service created (ID: {service_id})")
    else:
        error_msg = data.get("message", data.get("error", "Unknown error"))
        print(f"  [FAIL] Failed: {error_msg}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        print()
        print("MANUAL DEPLOYMENT RECOMMENDED:")
        print("Visit https://app.koyeb.com/ and deploy manually with these settings:")
        print(f"  - Repository: {GITHUB_REPO}")
        print(f"  - Branch: main")
        print(f"  - Dockerfile: Aethercore.Gateway/Dockerfile (context: repo root)")
        print(f"  - Instance: Nano (free, 0.1 vCPU / 512MB RAM / 2GB disk)")
        print(f"  - Routes: /aethercore -> 8000, /search -> 3000")
        sys.exit(1)

    # Step 3: Wait for deployment
    print()
    print("[3/4] Monitoring deployment...")
    print("  This may take 5-10 minutes for first build...")
    print()

    # Step 4: Show next steps
    print()
    print("[4/4] Deployment initiated!")
    print()
    print("Next steps:")
    print("1. Monitor at: https://app.koyeb.com/")
    print(f"2. Check logs: koyeb service logs {SERVICE_NAME} -f")
    print("3. Once deployed, get URL from Koyeb dashboard")
    print("4. Test: curl https://your-service.koyeb.app/health")
    print()


if __name__ == "__main__":
    main()
