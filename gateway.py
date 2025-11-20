"""
ProjectGPT HTTP Gateway - Full-Featured Production Server
Converts ProjectGPT (AetherCore) skills into REST API endpoints for Custom GPT Actions

Architecture:
- FastAPI server with automatic OpenAPI generation
- Dynamic skill loading from skills_config.json
- API key authentication with rate limiting
- OAuth-ready for future enterprise deployments
- Health checks and telemetry
- MCP-compatible tool calling patterns

Author: ProjectGPT Team
Version: 1.0.0
License: Proprietary
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uvicorn
import logging
import json
import os
from collections import defaultdict

# Local imports
from skill_loader import SkillLoader
from auth import AuthManager
from config import Config
from models import (
    ToolRequest,
    ToolResponse,
    HealthResponse,
    SkillInfo,
    ErrorResponse,
)

# ----------------------------------------------------------------------------
# Logging
# ----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# FastAPI App
# ----------------------------------------------------------------------------

app = FastAPI(
    title="ProjectGPT Gateway API",
    description="HTTP Gateway for ProjectGPT (AetherCore) Skills - Converts modular AI skills into REST endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for Custom GPT / Actions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://chatgpt.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------------
# Core Components
# ----------------------------------------------------------------------------

config = Config()
skill_loader = SkillLoader(config.skills_config_path)
auth_manager = AuthManager(config.api_keys)

# In-memory rate limit store (swap with Redis for production)
rate_limit_store = defaultdict(list)

security = HTTPBearer()

# ============================================================================
# RATE LIMITING
# ============================================================================


def check_rate_limit(api_key: str, limit: int = 100, window: int = 3600) -> bool:
    """
    Check if API key has exceeded rate limit.

    Args:
        api_key: API key identifier
        limit: Maximum requests per window
        window: Time window in seconds (default 1 hour)

    Returns:
        True if within limits, False if exceeded
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=window)

    # Clean old entries
    rate_limit_store[api_key] = [
        ts for ts in rate_limit_store[api_key] if ts > cutoff
    ]

    # Check limit
    if len(rate_limit_store[api_key]) >= limit:
        return False

    # Record request
    rate_limit_store[api_key].append(now)
    return True


# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verify API key from Authorization header.

    Returns:
        API key string if valid

    Raises:
        HTTPException: If authentication fails
    """
    api_key = credentials.credentials

    if not auth_manager.verify_key(api_key):
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Rate limit
    if not check_rate_limit(api_key):
        logger.warning(f"Rate limit exceeded for key: {api_key[:8]}...")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Max 100 requests per hour.",
        )

    return api_key


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns service status and loaded skills.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "skills_loaded": len(skill_loader.skills),
        "gateway_version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ProjectGPT HTTP Gateway",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "health": "/health",
    }


# ============================================================================
# SKILL DISCOVERY ENDPOINTS
# ============================================================================


@app.get("/skills", response_model=List[SkillInfo], tags=["Skills"])
async def list_skills(api_key: str = Depends(verify_api_key)):
    """
    List all available ProjectGPT (AetherCore) skills.

    Returns metadata for each loaded skill including:
    - Canonical name (e.g., 'AetherCore.DeepForge')
    - Version, description
    - Callable status
    - Execution priority
    - Available tools
    """
    skills_info: List[Dict[str, Any]] = []

    for skill_name, skill_config in skill_loader.skills.items():
        skills_info.append(
            {
                "name": skill_name,
                "version": skill_config.get("version", "unknown"),
                "description": skill_config.get("description", ""),
                "callable": skill_config.get("callable", False),
                "priority": skill_config.get("execution_priority", 99),
                "tools": skill_config.get("tools", []),
                "endpoint": f"/skills/{skill_name}",
                "dependencies": skill_config.get("dependencies", []),
                "metadata": skill_config.get("metadata", {}),
            }
        )

    return sorted(skills_info, key=lambda x: x["priority"])


@app.get("/skills/{skill_name}", response_model=SkillInfo, tags=["Skills"])
async def get_skill_info(
    skill_name: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Get detailed information about a specific skill.

    Args:
        skill_name: Skill identifier (alias or canonical).
                   Examples:
                    - 'deepforge' (alias)
                    - 'AetherCore.DeepForge' (canonical)

    Returns:
        Detailed skill metadata and capabilities.
    """
    # Resolve alias → canonical
    canonical_name = skill_loader._resolve_alias(skill_name)

    if canonical_name not in skill_loader.skills:
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{skill_name}' not found",
        )

    skill_config = skill_loader.skills[canonical_name]

    return {
        "name": canonical_name,
        "version": skill_config.get("version", "unknown"),
        "description": skill_config.get("description", ""),
        "callable": skill_config.get("callable", False),
        "priority": skill_config.get("execution_priority", 99),
        "tools": skill_config.get("tools", []),
        "endpoint": f"/skills/{canonical_name}",
        "dependencies": skill_config.get("dependencies", []),
        "metadata": skill_config.get("metadata", {}),
    }


# ============================================================================
# TOOL EXECUTION ENDPOINTS
# ============================================================================


@app.post(
    "/tools/{skill_name}/{tool_name}",
    response_model=ToolResponse,
    tags=["Tools"],
)
async def execute_tool(
    skill_name: str,
    tool_name: str,
    request: ToolRequest,
    api_key: str = Depends(verify_api_key),
):
    """
    Execute a specific tool from a ProjectGPT (AetherCore) skill.

    This is the main endpoint for Custom GPT Actions integration.

    Args:
        skill_name: Skill identifier (alias or canonical).
                    Examples:
                      - 'deepforge'
                      - 'AetherCore.DeepForge'
        tool_name: Tool name as declared in the skill config
                   (case-insensitive accepted).
        request: Tool parameters and context.

    Returns:
        Tool execution results with status and output.

    Examples:
        POST /tools/AetherCore.DeepForge/research
        POST /tools/deepforge/research
        POST /tools/marketsweep/scan
        POST /tools/promptfoundry/generate
    """
    # Resolve alias → canonical
    canonical_skill_name = skill_loader._resolve_alias(skill_name)

    # Validate skill exists
    if canonical_skill_name not in skill_loader.skills:
        raise HTTPException(
            status_code=404,
            detail=f"Skill '{skill_name}' not found",
        )

    skill_config = skill_loader.skills[canonical_skill_name]
    available_tools = skill_config.get("tools", [])

    # Case-insensitive tool resolution
    canonical_tool_name = None
    for t in available_tools:
        if t == tool_name or t.lower() == tool_name.lower():
            canonical_tool_name = t
            break

    if canonical_tool_name is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Tool '{tool_name}' not found in skill '{canonical_skill_name}'. "
                f"Available: {available_tools}"
            ),
        )

    # Log execution
    logger.info(
        f"Executing {canonical_skill_name}.{canonical_tool_name} "
        f"with params: {request.parameters}"
    )

    try:
        result = await skill_loader.execute_tool(
            skill_name=canonical_skill_name,
            tool_name=canonical_tool_name,
            parameters=request.parameters,
            context=request.context,
        )

        return {
            "success": True,
            "skill": canonical_skill_name,
            "tool": canonical_tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "execution_time_ms": result.get("_execution_time_ms", 0),
        }

    except HTTPException:
        # Let FastAPI's HTTPException handler catch this
        raise
    except Exception as e:
        logger.error(
            f"Tool execution failed: {canonical_skill_name}.{canonical_tool_name} - {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Tool execution failed: {str(e)}",
        )


# ============================================================================
# BULK TOOL EXECUTION (ORCHESTRATION)
# ============================================================================


@app.post("/orchestrate", response_model=Dict[str, Any], tags=["Orchestration"])
async def orchestrate_skills(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key),
):
    """
    Execute multiple tools in sequence with dependency resolution.

    Supports aliases and canonical skill names.

    Args:
        request: Orchestration plan with tool sequence.

    Returns:
        Combined results from all executed tools.

    Example:
        {
            "workflow": [
                {
                    "skill": "deepforge",
                    "tool": "research",
                    "params": {"query": "quantum computing"}
                },
                {
                    "skill": "promptfoundry",
                    "tool": "generate",
                    "params": {"role": "research_analyst"}
                }
            ]
        }
    """
    workflow = request.get("workflow", [])
    if not workflow:
        raise HTTPException(
            status_code=400,
            detail="Workflow cannot be empty",
        )

    results: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}

    for step in workflow:
        raw_skill_name = step.get("skill")
        raw_tool_name = step.get("tool")
        params = step.get("params", {}) or {}
        continue_on_error = step.get("continue_on_error", False)

        if not raw_skill_name or not raw_tool_name:
            results.append(
                {
                    "step": len(results) + 1,
                    "skill": raw_skill_name,
                    "tool": raw_tool_name,
                    "success": False,
                    "error": "Missing 'skill' or 'tool' in workflow step",
                }
            )
            if not continue_on_error:
                break
            else:
                continue

        # Resolve alias → canonical
        canonical_skill_name = skill_loader._resolve_alias(raw_skill_name)

        if canonical_skill_name not in skill_loader.skills:
            msg = f"Skill '{raw_skill_name}' not found (canonical: '{canonical_skill_name}')"
            logger.error(f"Orchestration step failed: {msg}")
            results.append(
                {
                    "step": len(results) + 1,
                    "skill": raw_skill_name,
                    "tool": raw_tool_name,
                    "success": False,
                    "error": msg,
                }
            )
            if not continue_on_error:
                break
            else:
                continue

        skill_config = skill_loader.skills[canonical_skill_name]
        available_tools = skill_config.get("tools", [])

        # Case-insensitive tool resolution
        canonical_tool_name = None
        for t in available_tools:
            if t == raw_tool_name or t.lower() == raw_tool_name.lower():
                canonical_tool_name = t
                break

        if canonical_tool_name is None:
            msg = (
                f"Tool '{raw_tool_name}' not found in skill '{canonical_skill_name}'. "
                f"Available: {available_tools}"
            )
            logger.error(f"Orchestration step failed: {msg}")
            results.append(
                {
                    "step": len(results) + 1,
                    "skill": raw_skill_name,
                    "tool": raw_tool_name,
                    "success": False,
                    "error": msg,
                }
            )
            if not continue_on_error:
                break
            else:
                continue

        try:
            # Inject prior context
            params["_context"] = context

            exec_result = await skill_loader.execute_tool(
                skill_name=canonical_skill_name,
                tool_name=canonical_tool_name,
                parameters=params,
                context=context,
            )

            # Update shared context
            context_key = f"{canonical_skill_name}.{canonical_tool_name}"
            context[context_key] = exec_result

            results.append(
                {
                    "step": len(results) + 1,
                    "skill": canonical_skill_name,
                    "tool": canonical_tool_name,
                    "success": True,
                    "result": exec_result,
                }
            )

        except Exception as e:
            logger.error(
                f"Orchestration step failed: {canonical_skill_name}.{canonical_tool_name} - {str(e)}"
            )
            results.append(
                {
                    "step": len(results) + 1,
                    "skill": canonical_skill_name,
                    "tool": canonical_tool_name,
                    "success": False,
                    "error": str(e),
                }
            )

            if not continue_on_error:
                break

    return {
        "success": all(r.get("success", False) for r in results),
        "steps_executed": len(results),
        "results": results,
        "final_context": context,
    }


# ============================================================================
# OPENAPI SPEC
# ============================================================================


@app.get("/openapi.json", tags=["System"])
async def get_openapi_spec():
    """
    Get OpenAPI specification for Custom GPT Actions.

    This spec can be imported into Custom GPT builder as:
    - Actions → Import from URL → <gateway-url>/openapi.json
    """
    return app.openapi()


# ============================================================================
# ERROR HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom error response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all error handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )


# ============================================================================
# TELEMETRY & MONITORING
# ============================================================================


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for monitoring."""
    start_time = datetime.now()

    response = await call_next(request)

    duration = (datetime.now() - start_time).total_seconds() * 1000

    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.2f}ms"
    )

    return response


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize gateway on startup."""
    logger.info("=" * 60)
    logger.info("ProjectGPT HTTP Gateway Starting...")
    logger.info("=" * 60)

    # Load skills
    skill_count = skill_loader.load_skills()
    logger.info(f"✓ Loaded {skill_count} skills")

    # List loaded skills
    for skill_name, cfg in skill_loader.skills.items():
        priority = cfg.get("execution_priority", 99)
        callable_flag = cfg.get("callable", False)
        tools_count = len(cfg.get("tools", []))
        logger.info(
            f"  • {skill_name} "
            f"(priority: {priority}, callable: {callable_flag}, tools: {tools_count})"
        )

    logger.info("=" * 60)
    logger.info("Gateway ready for requests")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("ProjectGPT HTTP Gateway shutting down...")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "gateway:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info",
    )
