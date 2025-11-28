"""
Pydantic Models for AetherCore Gateway (Aligned with AetherCore Skill Definitions)

Defines request/response schemas for:
- Tool execution
- Health checks
- Skill information
- Error responses
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


# ============================================================================
# TOOL EXECUTION MODELS
# ============================================================================

class ToolRequest(BaseModel):
    """
    Request model for tool execution

    Example:
        {
            "parameters": {"query": "compare GPUs", "limit": 5},
            "context": {"user_id": "u123", "session_id": "s456"}
        }
    """

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific parameters",
        examples=[{"query": "search term", "limit": 10}]
    )

    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional execution context (user info, session data, etc.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "parameters": {
                    "query": "best laptops 2025",
                    "max_results": 10
                },
                "context": {
                    "user_preference": "gaming",
                    "budget": 1500
                }
            }
        }


class ToolResponse(BaseModel):
    """
    Response model for tool execution

    Example:
        {
            "success": true,
            "skill": "AetherCore.DeepForge",
            "tool": "research",
            "result": {"findings": [...], "confidence": 0.92},
            "timestamp": "2025-01-15T10:30:00Z",
            "execution_time_ms": 214.5
        }
    """

    success: bool = Field(description="Whether tool executed successfully")

    skill: str = Field(description="Name of the skill that executed")

    tool: str = Field(description="Name of the tool that was executed")

    result: Dict[str, Any] = Field(description="Tool execution results")

    timestamp: str = Field(description="ISO timestamp of execution")

    execution_time_ms: float = Field(
        default=0,
        description="Execution time in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "skill": "AetherCore.DeepForge",
                "tool": "research",
                "result": {
                    "findings": ["Result 1", "Result 2"],
                    "confidence": 0.92
                },
                "timestamp": "2025-01-15T10:30:00Z",
                "execution_time_ms": 214.5
            }
        }


# ============================================================================
# SKILL INFORMATION MODELS
# ============================================================================

class SkillInfo(BaseModel):
    """
    Information about a ProjectGPT skill

    Example:
        {
            "name": "AetherCore.MarketSweep",
            "version": "3.1",
            "description": "Marketplace scanning and deal scoring engine",
            "callable": true,
            "priority": 4,
            "tools": ["scan", "compare", "validate", "score"],
            "endpoint": "/skills/AetherCore.MarketSweep",
            "dependencies": [],
            "metadata": {"category": "commerce"}
        }
    """

    name: str = Field(description="Canonical skill identifier")

    version: str = Field(description="Skill version")

    description: str = Field(
        description="Human-readable description of skill capabilities"
    )

    callable: bool = Field(
        description="Whether skill can be directly invoked by users"
    )

    priority: int = Field(
        description="Execution priority (0 = highest, 99 = lowest)"
    )

    tools: List[str] = Field(
        default_factory=list,
        description="Available tools within this skill"
    )

    endpoint: str = Field(
        description="API endpoint for this skill"
    )

    dependencies: Optional[List[str]] = Field(
        default=None,
        description="Other skills this skill depends on"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional skill metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "AetherCore.MarketSweep",
                "version": "3.1",
                "description": "Marketplace scanning and deal scoring engine",
                "callable": True,
                "priority": 4,
                "tools": ["scan", "compare", "validate", "score"],
                "endpoint": "/skills/AetherCore.MarketSweep",
                "dependencies": [],
                "metadata": {
                    "category": "commerce",
                    "marketplaces": 15
                }
            }
        }


# ============================================================================
# SYSTEM STATUS MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """
    Health check response

    Example:
        {
            "status": "healthy",
            "timestamp": "2025-01-15T10:30:00Z",
            "skills_loaded": 7,
            "gateway_version": "1.0.0"
        }
    """

    status: str = Field(
        description="Service health status",
        examples=["healthy", "degraded", "unhealthy"]
    )

    timestamp: str = Field(description="ISO timestamp of health check")

    skills_loaded: int = Field(
        description="Number of skills currently loaded"
    )

    gateway_version: str = Field(description="Gateway version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-15T10:30:00.000Z",
                "skills_loaded": 7,
                "gateway_version": "1.0.0"
            }
        }


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Error response model

    Example:
        {
            "error": true,
            "status_code": 404,
            "message": "Skill not found: AetherCore.Invalid",
            "timestamp": "2025-01-15T10:30:00Z",
            "details": {"available_skills": ["AetherCore.DeepForge", ...]}
        }
    """

    error: bool = Field(
        default=True,
        description="Always true for error responses"
    )

    status_code: int = Field(description="HTTP status code")

    message: str = Field(description="Human-readable error message")

    timestamp: str = Field(description="ISO timestamp of error")

    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "status_code": 404,
                "message": "Skill 'AetherCore.Invalid' not found",
                "timestamp": "2025-01-15T10:30:00.000Z",
                "details": {
                    "available_skills": [
                        "AetherCore.DeepForge",
                        "AetherCore.GeminiBridge",
                        "AetherCore.PromptFoundry"
                    ]
                }
            }
        }


# ============================================================================
# ORCHESTRATION MODELS
# ============================================================================

class OrchestrationStep(BaseModel):
    """Single step in an orchestration workflow"""

    skill: str = Field(description="Skill to execute")

    tool: str = Field(description="Tool to execute within the skill")

    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool parameters"
    )

    continue_on_error: bool = Field(
        default=False,
        description="Whether to continue workflow if this step fails"
    )


class OrchestrationRequest(BaseModel):
    """
    Request for multi-skill orchestration

    Example:
        {
            "workflow": [
                {
                    "skill": "AetherCore.DeepForge",
                    "tool": "research",
                    "params": {"query": "quantum computing"}
                },
                {
                    "skill": "AetherCore.PromptFoundry",
                    "tool": "generate",
                    "params": {"role": "research_analyst"}
                }
            ]
        }
    """

    workflow: List[OrchestrationStep] = Field(
        description="Sequence of tools to execute"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "workflow": [
                    {
                        "skill": "AetherCore.DeepForge",
                        "tool": "research",
                        "params": {"query": "quantum computing"},
                        "continue_on_error": False
                    },
                    {
                        "skill": "AetherCore.PromptFoundry",
                        "tool": "generate",
                        "params": {"preset": "scientist"},
                        "continue_on_error": True
                    }
                ]
            }
        }
