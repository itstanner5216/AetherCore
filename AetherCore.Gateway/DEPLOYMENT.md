# AetherCore Gateway - Koyeb Deployment Guide

## Quick Deploy (Manual - Recommended)

### Prerequisites
- Koyeb account (free): https://app.koyeb.com/
- GitHub account connected to Koyeb

### Step-by-Step Deployment

1. **Login to Koyeb**
   - Go to https://app.koyeb.com/
   - Connect your GitHub account if not already connected

2. **Create Web Service**
   - Click **"Create Web Service"**
   - Select **"GitHub"** as the source
   - Choose **Docker** explicitly (the repo layout prevents autodetection)

3. **Repository Settings**
   ```
Repository: itstanner5216/AetherCore
Branch: main
Builder: Dockerfile
Docker build context: /        # repo root so Gateway + skills are visible
Dockerfile path: Aethercore.Gateway/Dockerfile
```

4. **Instance Configuration**
   ```
   Service name: aethercore-gateway
   Instance type: Nano (0.1 vCPU / 512MB RAM / 2GB disk) - Free Tier
   Region: Washington D.C. (was)   # only free region
   Scaling: Min 1, Max 1
   ```

5. **Port Configuration (Advanced → Service ports)**
   ```
External path prefix  Target internal port  Protocol
/aethercore          8000                   HTTP   # FastAPI
/search              3000                   HTTP   # Node helper
```
- Both ports share the same service URL; the path prefix maps requests to the correct process.

6. **Environment Variables**

   Click "Add Environment Variable" and add (no secrets shown):

   ```bash
   ENVIRONMENT=production
   DEBUG=false
   PORT=8000
   HOST=0.0.0.0
   LOG_LEVEL=INFO
   CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=3600
   SKILLS_CONFIG_PATH=../AetherCore.System/skills_config.json

   # Gateway + helper auth (must match)
   API_KEY=your_gateway_api_key
   GATEWAY_API_KEY=your_gateway_api_key

   # Search helper URL (internal)
   SEARCH_ENGINE_SERVER_URL=http://localhost:3000

   # Upstash Redis (required for quotas)
   UPSTASH_REDIS_REST_URL=your_upstash_url
   UPSTASH_REDIS_REST_TOKEN=your_upstash_token

   # Provider keys (optional but recommended)
   GOOGLE_API_KEY=...
   GOOGLE_CSE_ID=...
   BRAVE_API=...
   SERPER_API_KEY=...
   WEBSCRAPING_API_KEY=...
   SCRAPINGANT_API_KEY=...
   ```

7. **Health Check**
   ```
   Path: /health   # container path; externally /aethercore/health
   Port: 8000
   Grace period: 60 seconds
   Interval: 30 seconds
   ```

8. **Deploy**
   - Click **"Deploy"**
   - Wait 5-10 minutes for build to complete
   - Monitor in Koyeb dashboard

9. **Get Your URL**
   - The service domain will be shown by Koyeb, e.g. `https://aethercore-gateway-[org].koyeb.app`
   - FastAPI base: `https://.../aethercore`
   - Search helper base: `https://.../search`

10. **Test Deployment**
    ```bash
    curl https://your-service.koyeb.app/aethercore/health
    curl -H "Authorization: Bearer $API_KEY" https://your-service.koyeb.app/search/api/quotas
    ```

---

## Automated Deploy (CLI - Optional)

### Install Koyeb CLI

**macOS:**
```bash
brew install koyeb/tap/koyeb-cli
```

**Linux:**
```bash
curl -fsSL https://app.koyeb.com/install.sh | bash
```

**Windows:**
```powershell
scoop install koyeb-cli
```

### Deploy with CLI

```bash
# Set API token
export KOYEB_TOKEN="your-koyeb-api-key"

# Run deployment script
bash koyeb_deploy.sh
```

OR use the Python script:
```bash
python deploy.py
```

---

## Update Deployment

### Via Dashboard
1. Go to https://app.koyeb.com/
2. Find `aethercore-gateway` service
3. Click "Redeploy" to pull latest from GitHub

### Via CLI
```bash
koyeb service redeploy aethercore-gateway
```

---

## Monitoring

### View Logs
```bash
koyeb service logs aethercore-gateway -f
```

### Check Status
```bash
koyeb service get aethercore-gateway
```

### Dashboard
https://app.koyeb.com/services/aethercore-gateway

---

## Troubleshooting

### Build Fails
- Check Koyeb logs for Docker build errors
- Verify Dockerfile path is set to `Aethercore.Gateway/Dockerfile` with context `/`
- Ensure all dependencies in requirements.txt

### Service Won't Start
- Check environment variables are set correctly
- Verify ports 8000 and 3000 are exposed and mapped to /aethercore and /search
- Check health check endpoint returns 200

### Out of Memory
- Reduce workers in Dockerfile from 2 to 1
- Consider upgrading instance (still free: Eco - 1GB RAM)

### Health Check Failing
- Increase grace period to 90 seconds
- Check `/health` endpoint locally first
- Verify uvicorn binds to 0.0.0.0, not 127.0.0.1

### Render still deploying
- Disable or lock the Render service, or remove its GitHub webhook, so only Koyeb redeploys on push
- Remove any Render-specific GitHub Actions if they auto-trigger builds

---

## Free Tier Limits

- **Services**: 2 web services
- **Instance**: Nano (512MB RAM, 0.1 vCPU shared)
- **Bandwidth**: Unlimited
- **Build time**: Unlimited
- **Auto-sleep**: After 30min inactivity
- **Custom domains**: 1 per service

---

## Next Steps After Deployment

1. **Test all endpoints**
   ```bash
   curl https://your-service.koyeb.app/aethercore/health
   curl https://your-service.koyeb.app/aethercore/docs
   curl https://your-service.koyeb.app/aethercore/openapi.json
   curl -H "Authorization: Bearer $API_KEY" https://your-service.koyeb.app/search/api/quotas
   ```

2. **Update Custom GPT**
   - Import OpenAPI spec from: `https://your-service.koyeb.app/openapi.json`
   - Configure Bearer token auth with your API_KEY

3. **Update Repository Files**
   - Replace placeholder URLs in openapi_schema.json
   - Update CustomInstructions_with_bootstrap_v3.yaml
   - Commit and push changes

---

## Support

- **Koyeb Docs**: https://www.koyeb.com/docs
- **Koyeb Support**: https://www.koyeb.com/support
- **Dashboard**: https://app.koyeb.com/

---

**Note**: Manual deployment through the Koyeb dashboard is the most reliable method for first-time setup. The CLI and API can be used for subsequent redeployments.
