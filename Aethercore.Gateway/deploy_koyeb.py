#!/usr/bin/env python3
"""
Koyeb Deployment Script for AetherCore Gateway

Automates deployment to Koyeb's free tier using the Koyeb REST API.

Usage:
    python deploy_koyeb.py
"""

import os
import json
import requests
import sys
import time
from typing import Dict, Any

# Configuration from environment
KOYEB_API_KEY = os.getenv("KOYEB_API_KEY", "5ue0i50v18viyfdrjgm7rea3x7xnjeqe3h57z0idxh7o62vdq9oiyux5y7b5kfjf").strip()
GITHUB_REPO = "github.com/itstanner5216/AetherCore"
SERVICE_NAME = "aethercore-gateway"
APP_NAME = "aethercore"

# Environment variables for the service
SERVICE_ENV_VARS = [
    {"key": "ENVIRONMENT", "value": "production"},
    {"key": "DEBUG", "value": "false"},
    {"key": "PORT", "value": "8000"},
    {"key": "HOST", "value": "0.0.0.0"},
    {"key": "LOG_LEVEL", "value": "INFO"},
    {"key": "CORS_ORIGINS", "value": "https://chat.openai.com,https://chatgpt.com"},
    {"key": "RATE_LIMIT_REQUESTS", "value": "100"},
    {"key": "RATE_LIMIT_WINDOW", "value": "3600"},
    {"key": "SKILLS_CONFIG_PATH", "value": "skills_config.json"},
    {"key": "API_KEY", "value": "f3a0c4b7e1d9c0f247a6df81b2439e57c1d84e3ab9a92f7db08f6c2cd41e5af0"},
    {"key": "GOOGLE_API_KEY", "value": "AIzaSyDLSW6qz4tC9Aq0p2yO0gbmrrIBeKjGdBs"},
    {"key": "GOOGLE_CSE_ID", "value": "739bdcbb2b51b4409"},
    {"key": "BRAVE_API", "value": "BSAUZcHnbsKgi9GTsu4wQV2SPEeZ3wy"},
    {"key": "SERPER_API_KEY", "value": "8b0733a1da1ace1e16a34f5a396b48e4daa4d88e"},
    {"key": "WEBSCRAPING_API_KEY", "value": "DXXGG7k1XgDQI1EPvq2ZCobU3N1uksPo"},
    {"key": "SCRAPINGANT_API_KEY", "value": "0f53dcf52bc3454687ff777304dbd583"},
]

API_BASE = "https://app.koyeb.com/v1"


def make_request(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict:
    """Make authenticated request to Koyeb API"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {KOYEB_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n[{method}] {endpoint}")

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            print(f"Payload keys: {list(data.keys()) if data else 'None'}")
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")

        print(f"Status: {response.status_code}")

        if response.status_code >= 400:
            print(f"Error Response: {response.text}")

        return response.json() if response.text else {}

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}


def check_app():
    """Check if app exists"""
    print("\n=== Checking App ===")
    result = make_request("GET", "/apps")

    if "apps" in result:
        for app in result["apps"]:
            if app["name"] == APP_NAME:
                print(f"[OK] App '{APP_NAME}' found (ID: {app['id']})")
                return app["id"]

    print(f"[INFO] App '{APP_NAME}' not found, will create")
    return None


def create_app():
    """Create a new app"""
    print("\n=== Creating App ===")

    app_config = {
        "name": APP_NAME,
    }

    result = make_request("POST", "/apps", app_config)

    if "app" in result:
        app_id = result["app"]["id"]
        print(f"[OK] App '{APP_NAME}' created (ID: {app_id})")
        return app_id
    else:
        print(f"[FAIL] Failed to create app")
        return None


def create_service(app_id: str):
    """Create a new service"""
    print("\n=== Creating Service ===")

    service_config = {
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
                "dockerfile": "Dockerfile",
                "target": ""
            },
            "instance_types": [{
                "type": "nano"
            }],
            "ports": [{
                "port": 8000,
                "protocol": "http"
            }],
            "routes": [{
                "port": 8000,
                "path": "/"
            }],
            "env": SERVICE_ENV_VARS,
            "health_checks": [{
                "http": {
                    "port": 8000,
                    "path": "/health",
                    "interval": "30s",
                    "timeout": "10s"
                }
            }],
            "scalings": [{
                "min": 1,
                "max": 1
            }],
            "deployments": 1
        }
    }

    result = make_request("POST", "/services", service_config)

    if "service" in result:
        service = result["service"]
        print(f"[OK] Service '{SERVICE_NAME}' created")
        print(f"Service ID: {service['id']}")
        return service
    else:
        print(f"[FAIL] Failed to create service")
        print(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
        return None


def get_service_status(service_id: str):
    """Get service status and URL"""
    print("\n=== Getting Service Status ===")
    result = make_request("GET", f"/services/{service_id}")

    if "service" in result:
        service = result["service"]
        status = service.get("status", "unknown")

        # Extract public URL from active deployment
        public_url = None
        if "active_deployment" in service:
            deployment = service["active_deployment"]
            if "deployment_urls" in deployment and deployment["deployment_urls"]:
                public_url = f"https://{deployment['deployment_urls'][0]}"

        print(f"[OK] Service found")
        print(f"  Status: {status}")
        print(f"  Public URL: {public_url or 'Not yet available'}")

        return {
            "status": status,
            "url": public_url
        }
    else:
        print(f"[FAIL] Service not found")
        return None


def main():
    """Main deployment flow"""
    print("=" * 60)
    print("AetherCore Gateway - Koyeb Deployment (Free Tier)")
    print("=" * 60)

    if not KOYEB_API_KEY:
        print("\n[FAIL] Error: KOYEB_API_KEY not set")
        sys.exit(1)

    print(f"\nGitHub Repo: {GITHUB_REPO}")
    print(f"App Name: {APP_NAME}")
    print(f"Service Name: {SERVICE_NAME}")
    print(f"Instance Type: Nano (Free Tier)")

    # Step 1: Check/create app
    app_id = check_app()
    if not app_id:
        app_id = create_app()
        if not app_id:
            print("\n[FAIL] Could not create app")
            sys.exit(1)

    # Step 2: Create service
    service = create_service(app_id)

    if not service:
        print("\n[FAIL] Deployment failed")
        sys.exit(1)

    service_id = service["id"]

    # Step 3: Wait for deployment
    print("\n=== Waiting for Deployment ===")
    print("This may take 5-10 minutes for initial build...")

    max_wait = 600  # 10 minutes
    wait_interval = 30  # Check every 30 seconds
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(wait_interval)
        elapsed += wait_interval

        status_info = get_service_status(service_id)

        if status_info:
            status = status_info["status"]
            url = status_info["url"]

            if status == "HEALTHY" and url:
                print(f"\n[OK] Service is live!")
                print(f"\nPublic URL: {url}")
                print(f"\nEndpoints to test:")
                print(f"  - {url}/health")
                print(f"  - {url}/docs")
                print(f"  - {url}/openapi.json")
                return url

            elif status in ["STARTING", "DEPLOYING"]:
                print(f"[INFO] Status: {status} (waited {elapsed}s)")
            elif status == "ERROR":
                print(f"[FAIL] Deployment failed with error status")
                print(f"Check Koyeb dashboard for details: https://app.koyeb.com/")
                sys.exit(1)

    print(f"\n[WARN] Deployment taking longer than expected")
    print(f"Check status at: https://app.koyeb.com/")
    print(f"Service ID: {service_id}")


if __name__ == "__main__":
    main()
