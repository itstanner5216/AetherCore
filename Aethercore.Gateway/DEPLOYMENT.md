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

3. **Repository Settings**
   ```
   Repository: itstanner5216/AetherCore
   Branch: main
   Builder: Dockerfile
   Dockerfile path: /Dockerfile
   ```

4. **Instance Configuration**
   ```
   Service name: aethercore-gateway
   Instance type: Nano (512MB RAM - Free Tier)
   Region: Washington D.C. (was) OR Frankfurt (fra)
   Scaling: Min 1, Max 1
   ```

5. **Port Configuration**
   ```
   Port: 8000
   Protocol: HTTP
   ```

6. **Environment Variables**

   Click "Add Environment Variable" and add each of these:

   ```bash
   ENVIRONMENT=production
   DEBUG=false
   PORT=8000
   HOST=0.0.0.0
   LOG_LEVEL=INFO
   CORS_ORIGINS=https://chat.openai.com,https://chatgpt.com
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=3600
   SKILLS_CONFIG_PATH=skills_config.json

   # Gateway API Key
   API_KEY=f3a0c4b7e1d9c0f247a6df81b2439e57c1d84e3ab9a92f7db08f6c2cd41e5af0

   # Google APIs
   GOOGLE_API_KEY=AIzaSyDLSW6qz4tC9Aq0p2yO0gbmrrIBeKjGdBs
   GOOGLE_CSE_ID=739bdcbb2b51b4409

   # Search APIs
   BRAVE_API=BSAUZcHnbsKgi9GTsu4wQV2SPEeZ3wy
   SERPER_API_KEY=8b0733a1da1ace1e16a34f5a396b48e4daa4d88e

   # Scraping APIs
   WEBSCRAPING_API_KEY=DXXGG7k1XgDQI1EPvq2ZCobU3N1uksPo
   SCRAPINGANT_API_KEY=0f53dcf52bc3454687ff777304dbd583
   ```

7. **Health Check**
   ```
   Path: /health
   Port: 8000
   Grace period: 60 seconds
   Interval: 30 seconds
   ```

8. **Deploy**
   - Click **"Deploy"**
   - Wait 5-10 minutes for build to complete
   - Monitor in Koyeb dashboard

9. **Get Your URL**
   - Once deployed, Koyeb shows the public URL
   - Format: `https://aethercore-gateway-[your-org].koyeb.app`

10. **Test Deployment**
    ```bash
    curl https://your-service.koyeb.app/health
    ```

    Expected response:
    ```json
    {
      "status": "healthy",
      "timestamp": "2025-...",
      "skills_loaded": 10,
      "gateway_version": "1.0.0"
    }
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
- Verify Dockerfile is in repository root
- Ensure all dependencies in requirements.txt

### Service Won't Start
- Check environment variables are set correctly
- Verify port 8000 is exposed
- Check health check endpoint returns 200

### Out of Memory
- Reduce workers in Dockerfile from 2 to 1
- Consider upgrading instance (still free: Eco - 1GB RAM)

### Health Check Failing
- Increase grace period to 90 seconds
- Check `/health` endpoint locally first
- Verify uvicorn binds to 0.0.0.0, not 127.0.0.1

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
   curl https://your-service.koyeb.app/
   curl https://your-service.koyeb.app/health
   curl https://your-service.koyeb.app/docs
   curl https://your-service.koyeb.app/openapi.json
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
