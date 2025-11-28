# AetherCore Gateway API

ProjectGPT is a modular skillset ecosystem with an HTTP Gateway that exposes AetherCore skills as REST API endpoints. This enables Custom GPT Actions integration, allowing OpenAI GPTs to access sophisticated research, search, commerce, and reasoning capabilities through standard HTTP requests.

## Overview

This repository contains:

- **HTTP Gateway (FastAPI)**: REST API server with automatic OpenAPI generation
- **10 Modular Skills**: Autonomous capabilities for research, search, commerce, reasoning, and more
- **Event-Driven Architecture**: Skills communicate via messaging bus for complex workflows
- **OpenAI Custom GPT Integration**: Direct integration via Actions and outbound connections
- **Koyeb Deployment**: Production-ready containerized deployment on free tier

### Key Features

- **Modular Design**: Skills can be loaded individually or in combination
- **Event-Driven Architecture**: Skills communicate through a messaging bus and automation graph
- **REST API Gateway**: FastAPI server with automatic OpenAPI spec generation
- **Custom GPT Actions**: Direct integration with OpenAI Custom GPT via Actions
- **Authentication**: API key-based authentication with rate limiting
- **Automatic Telemetry**: File-based logging for skill execution and error tracking
- **Scalable Workflows**: Supports complex multi-stage automation pipelines
- **Free Deployment**: Runs completely free on Koyeb's Starter plan

## Skills Included

The repository includes 10 AetherCore skills:

### Core Infrastructure (Priority 0-2)

- **AetherCore.Orchestrator** - Root controller for skill routing, scheduling, and synthesis
- **AetherCore.EventMesh** - Event routing fabric for inter-skill communication
- **AetherCore.OptiGraph** - Performance optimization and quality validation

### Callable Skills (Priority 3-9)

- **AetherCore.DeepForge** - Advanced research engine with source validation
- **AetherCore.MarketSweep** - E-commerce product search and comparison
- **AetherCore.GeminiBridge** - Gemini API integration for fallback/crosscheck
- **AetherCore.PromptFoundry** - Dynamic prompt generation system
- **AetherCore.SearchEngine** - Multi-provider web search (Google, Brave, Serper) + scraping
- **AetherCore.ReasoningChain** - Chain-of-thought reasoning with verification
- **AetherCore.SourceValidator** - Source credibility scoring and citation

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Koyeb account (free tier available)

### Local Development

1. Clone the repository
2. Copy environment template:
   ```bash
   cp dev.env.example dev.env
   ```
3. Fill in your API keys in `dev.env`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the gateway:
   ```bash
   uvicorn gateway:app --reload --port 8000
   ```
6. Access the docs at: http://localhost:8000/docs

## Deployment to Koyeb (100% Free)

### Why Koyeb?

- **Free Tier**: 2 web services, 2 GB RAM, 2 vCPU shared
- **No Credit Card Required**: Truly free deployment
- **Auto-scaling**: Scales to zero when not in use
- **Global CDN**: Fast response times worldwide
- **GitHub Integration**: Auto-deploy on push

### Automated Deployment

This project is configured for automatic deployment to Koyeb from GitHub:

1. **Create Koyeb Account**
   - Sign up at https://app.koyeb.com (no credit card required)
   - Connect your GitHub account

2. **Deploy from GitHub**
   - In Koyeb dashboard, click "Create Web Service"
   - Select "GitHub" as source
   - Choose repository: `itstanner5216/AetherCore`
   - Branch: `main`
   - Build type: Dockerfile
   - Instance type: **Nano (free tier)**
   - Regions: Choose any free region (e.g., Washington D.C.)
   - Port: `8000`

3. **Configure Environment Variables**
   Add these in Koyeb dashboard under "Environment":

   ```
   ENVIRONMENT=production
   DEBUG=false
   PORT=8000
   API_KEY=your_gateway_api_key
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_google_cse_id
   BRAVE_API=your_brave_api_key
   SERPER_API_KEY=your_serper_api_key
   WEBSCRAPING_API_KEY=your_webscraping_api_key
   SCRAPINGANT_API_KEY=your_scrapingant_api_key
   ```

4. **Deploy**
   - Click "Deploy"
   - Koyeb automatically builds the Docker container
   - Health checks ensure service availability at `/health`
   - Your API is live at: `https://your-service-name.koyeb.app`

### Manual Deployment

```bash
# Build Docker image
docker build -t aethercore-gateway .

# Run locally
docker run -p 8000:8000 --env-file dev.env aethercore-gateway

# Test health endpoint
curl http://localhost:8000/health
```

## API Endpoints

### System Endpoints

- `GET /` - API information
- `GET /health` - Health check (public)
- `GET /docs` - Interactive API documentation
- `GET /openapi.json` - OpenAPI spec for Custom GPT Actions

### Skill Endpoints

- `GET /skills` - List all available skills (requires auth)
- `GET /skills/{skill_name}` - Get skill details (requires auth)
- `POST /tools/{skill_name}/{tool_name}` - Execute skill tool (requires auth)
- `POST /orchestrate` - Execute multi-skill workflows (requires auth)

### Monitoring

- `GET /logs` - View telemetry logs (requires auth)

## Custom GPT Integration

### Step 1: Deploy to Koyeb

Follow the deployment instructions above to get your live API URL.

### Step 2: Import OpenAPI Spec

1. Open Custom GPT builder in ChatGPT
2. Go to **Actions** → **Import from URL**
3. Enter: `https://your-service-name.koyeb.app/openapi.json`
4. Configure authentication with your API key

### Step 3: Test Integration

Example Custom GPT prompt:

```
Search for "best laptops 2025" using the searchengine skill
```

The GPT will call:

```
POST /tools/searchengine/search
{
  "parameters": {
    "query": "best laptops 2025",
    "max_results": 10
  }
}
```

## Authentication

All endpoints (except `/health` and `/`) require Bearer token authentication:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-service-name.koyeb.app/skills
```

## Architecture

### Core Components

- **Skill Registry**: Manages loaded skills and their metadata
- **Messaging Bus**: Handles event routing between skills
- **Automation Graph**: Orchestrates complex workflows and dependencies
- **Telemetry Logger**: Automatic file-based logging (no GPT involvement)

### Execution Model

Skills operate independently while coordinating via the EventMesh. The Orchestrator routes requests, manages dependencies, and synthesizes outputs from multiple skills.

## Development

### Project Structure

```
Aethercore/
├── gateway.py              # FastAPI application
├── skill_loader.py         # Skill loading and execution
├── config.py               # Configuration management
├── auth.py                 # Authentication manager
├── models.py               # Pydantic models
├── skills_config.json      # Skill definitions
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── skills/                 # Individual skill implementations
```

### Adding New Skills

1. Add skill configuration to `skills_config.json`
2. Implement skill handler in `skill_loader.py`
3. Update API documentation
4. Test locally before deploying

## Environment Variables

See [dev.env.example](dev.env.example) for all required environment variables.

### Required

- `API_KEY` - Gateway authentication key
- `GOOGLE_API_KEY` - Google API key (for Gemini and CSE)
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID

### Optional

- `BRAVE_API` - Brave Search API key
- `SERPER_API_KEY` - Serper API key
- `WEBSCRAPING_API_KEY` - Webscraping.ai API key
- `SCRAPINGANT_API_KEY` - ScrapingAnt API key

## Monitoring & Logs

Telemetry is automatically logged to `logs/` directory:

- `logs/telemetry.jsonl` - Skill execution metrics
- `logs/errors.jsonl` - Error tracking

Access logs via the API:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-service-name.koyeb.app/logs?limit=50&log_type=all
```

## Rate Limiting

Default rate limits:

- 100 requests per hour per API key
- Rate limit headers included in responses
- 429 status code when limit exceeded

## Koyeb Free Tier Limits

- **Web Services**: 2 services
- **Instances**: Nano (512MB RAM, 0.1 vCPU)
- **Build Time**: Unlimited
- **Bandwidth**: Unlimited data transfer
- **Auto-sleep**: Services sleep after 30min inactivity, wake on first request
- **Custom Domains**: 1 custom domain per service

## Troubleshooting

### Service Won't Start

- Check environment variables are set correctly
- Verify Dockerfile builds locally first
- Check Koyeb logs for specific errors

### Health Check Failing

- Ensure port 8000 is exposed
- Verify `/health` endpoint returns 200 status
- Check that uvicorn is binding to 0.0.0.0, not localhost

### Out of Memory

- Reduce `--workers` in Dockerfile CMD to 1 for Nano instances
- Consider upgrading to Eco instance if needed (still free)

## Support

For issues or questions:

- Check individual skill documentation in `skills/` directory
- Review API documentation at `/docs` endpoint
- Check Koyeb deployment logs
- Ensure all environment variables are configured

## License

This skill ecosystem is designed for use with OpenAI Custom GPT and similar AI platforms. Refer to your license terms for usage guidelines.

---

**Note**: This system exposes AetherCore skills as REST API endpoints, enabling complex automation while maintaining compatibility with OpenAI Custom GPT Actions and other HTTP clients. Deployed completely free on Koyeb's Starter plan.
