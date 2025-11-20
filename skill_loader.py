"""
Skill Loader (AetherCore-Aligned)

Supports:
- Dynamic skill discovery
- Alias → canonical skill name mapping
- Tool execution routing
- Skill-specific execution handlers
- Generic fallback handler

Compatible with updated AetherCore skills:
- AetherCore.Orchestrator
- AetherCore.EventMesh
- AetherCore.OptiGraph
- AetherCore.DeepForge
- AetherCore.MarketSweep
- AetherCore.GeminiBridge
- AetherCore.PromptFoundry
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillLoader:
    """
    Dynamic skill loader with alias mapping for AetherCore skills.
    """

    # ============================================================
    # ALIAS MAP — Option B (canonical name routing)
    # ============================================================

    ALIAS_MAP: Dict[str, str] = {
        # Orchestrator
        "orchestrator": "AetherCore.Orchestrator",
        "core-orchestrator": "AetherCore.Orchestrator",

        # EventMesh
        "eventmesh": "AetherCore.EventMesh",
        "mesh": "AetherCore.EventMesh",
        "event-mesh": "AetherCore.EventMesh",

        # OptiGraph
        "optigraph": "AetherCore.OptiGraph",
        "optimizer": "AetherCore.OptiGraph",
        "optimization": "AetherCore.OptiGraph",

        # DeepForge
        "deepforge": "AetherCore.DeepForge",
        "deep-forge": "AetherCore.DeepForge",
        "research": "AetherCore.DeepForge",

        # MarketSweep
        "marketsweep": "AetherCore.MarketSweep",
        "market-sweep": "AetherCore.MarketSweep",
        "commerce": "AetherCore.MarketSweep",
        "deals": "AetherCore.MarketSweep",

        # GeminiBridge
        "geminibridge": "AetherCore.GeminiBridge",
        "gemini-bridge": "AetherCore.GeminiBridge",
        "gemini": "AetherCore.GeminiBridge",
        "hybrid": "AetherCore.GeminiBridge",

        # PromptFoundry
        "promptfoundry": "AetherCore.PromptFoundry",
        "prompt-foundry": "AetherCore.PromptFoundry",
        "prompts": "AetherCore.PromptFoundry",
        "factory": "AetherCore.PromptFoundry",
    }

    # ============================================================

    def __init__(self, config_path: str = "skills_config.json"):
        self.config_path = config_path
        self.skills: Dict[str, Dict] = {}
        self.skill_handlers: Dict[str, Any] = {}

    # ============================================================
    # LOAD SKILLS
    # ============================================================

    def load_skills(self) -> int:
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            skills_data = config.get("skills", {})

            for alias_or_name, skill_cfg in skills_data.items():
                canonical = self._resolve_alias(alias_or_name)
                self.skills[canonical] = skill_cfg
                logger.info(f"Loaded skill: {canonical}")

            # Sort by execution priority
            self.skills = dict(
                sorted(
                    self.skills.items(),
                    key=lambda x: x[1].get("execution_priority", 99)
                )
            )

            return len(self.skills)

        except FileNotFoundError:
            logger.error(f"Skills config not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in skills config: {e}")
            raise

    # ============================================================
    # SKILL EXECUTION
    # ============================================================

    def _resolve_alias(self, name: str) -> str:
        """
        Convert alias → canonical skill name
        """
        normalized = name.strip().lower()
        return self.ALIAS_MAP.get(normalized, name)

    async def execute_tool(
        self,
        skill_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:

        start_time = datetime.now()

        # Resolve alias → canonical
        canonical_name = self._resolve_alias(skill_name)

        if canonical_name not in self.skills:
            raise ValueError(f"Skill not found: {canonical_name}")

        # ============================================================
        # CANONICAL ROUTING
        # ============================================================

        if canonical_name == "AetherCore.Orchestrator":
            result = await self._execute_orchestrator(tool_name, parameters, context)

        elif canonical_name == "AetherCore.EventMesh":
            result = await self._execute_eventmesh(tool_name, parameters, context)

        elif canonical_name == "AetherCore.OptiGraph":
            result = await self._execute_optigraph(tool_name, parameters, context)

        elif canonical_name == "AetherCore.DeepForge":
            result = await self._execute_deepforge(tool_name, parameters, context)

        elif canonical_name == "AetherCore.MarketSweep":
            result = await self._execute_marketsweep(tool_name, parameters, context)

        elif canonical_name == "AetherCore.GeminiBridge":
            result = await self._execute_geminibridge(tool_name, parameters, context)

        elif canonical_name == "AetherCore.PromptFoundry":
            result = await self._execute_promptfoundry(tool_name, parameters, context)

        else:
            result = await self._execute_generic_skill(
                canonical_name, tool_name, parameters, context
            )

        # Add execution metadata
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        result["_execution_time_ms"] = round(execution_time, 2)
        result["_skill"] = canonical_name
        result["_tool"] = tool_name

        return result

    # ============================================================
    # SKILL-SPECIFIC HANDLERS
    # ============================================================

    # -------------------------------
    # ORCHESTRATOR
    # -------------------------------

    async def _execute_orchestrator(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "route":
            return {
                "routing": {
                    "chosen_skill": "AetherCore.DeepForge",
                    "expected_runtime_ms": 5000
                }
            }
        elif tool == "schedule":
            return {
                "priority_order": list(self.skills.keys())
            }
        elif tool == "synthesize":
            return {
                "synthesis": "Merged output",
                "sources": len(context or {})
            }
        else:
            raise ValueError(f"Unknown Orchestrator tool: {tool}")

    # -------------------------------
    # EVENT MESH
    # -------------------------------

    async def _execute_eventmesh(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "emit":
            return {
                "event": parameters.get("event"),
                "emitted": True
            }

        elif tool == "subscribe":
            return {
                "subscription": parameters.get("channel", "default"),
                "status": "subscribed"
            }

        elif tool == "dispatch":
            return {
                "destination_skill": parameters.get("target"),
                "delivered": True
            }

        else:
            raise ValueError(f"Unknown EventMesh tool: {tool}")


    # -------------------------------
    # OPTIGRAPH
    # -------------------------------

    async def _execute_optigraph(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "optimize":
            return {"status": "optimized"}
        elif tool == "validate":
            return {"valid": True, "quality_score": 0.96}
        elif tool == "telemetry":
            return {"runtime_ms": 123.4}
        else:
            raise ValueError(f"Unknown OptiGraph tool: {tool}")

    # -------------------------------
    # DEEPFORGE
    # -------------------------------

    async def _execute_deepforge(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "research":
            q = parameters.get("query", "")
            return {
                "query": q,
                "findings": [f"Finding related to {q}"],
                "confidence": 0.94
            }
        elif tool == "analyze":
            return {"analysis": "deep forensic analysis", "confidence": 0.91}
        elif tool == "verify":
            return {"verification": True}
        elif tool == "synthesize":
            return {"synthesis": "Final combined narrative"}
        else:
            raise ValueError(f"Unknown DeepForge tool: {tool}")

    # -------------------------------
    # MARKETSWEEP
    # -------------------------------

    async def _execute_marketsweep(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "scan":
            product = parameters.get("query", "")
            return {"product": product, "platforms_scanned": 15}
        elif tool == "compare":
            return {"lowest_price": 299.99}
        elif tool == "validate":
            return {"valid": True}
        elif tool == "score":
            return {"deal_score": 0.93}
        else:
            raise ValueError(f"Unknown MarketSweep tool: {tool}")

    # -------------------------------
    # GEMINI BRIDGE
    # -------------------------------

    async def _execute_geminibridge(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "escalate":
            return {"escalated": True, "response": "Gemini fallback output"}
        elif tool == "crosscheck":
            return {"crosscheck": True, "agreement": 0.91}
        elif tool == "debug":
            return {"diagnostics": "Gemini-assisted debugging results"}
        elif tool == "alternatives":
            return {"alternatives": ["Approach A", "Approach B"]}
        else:
            raise ValueError(f"Unknown GeminiBridge tool: {tool}")

    # -------------------------------
    # PROMPT FOUNDRY
    # -------------------------------

    async def _execute_promptfoundry(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "generate":
            role = parameters.get("role", "general")
            return {
                "role": role,
                "prompt": f"You are a {role}..."
            }
        elif tool == "presets":
            return {"presets": ["engineer", "doctor", "analyst"]}
        elif tool == "validate":
            return {"valid": True}
        elif tool == "export":
            return {"format": parameters.get("format", "chatgpt")}
        else:
            raise ValueError(f"Unknown PromptFoundry tool: {tool}")

    # -------------------------------
    # GENERIC
    # -------------------------------

    async def _execute_generic_skill(
        self,
        skill_name: str,
        tool_name: str,
        parameters: Dict,
        context: Optional[Dict]
    ) -> Dict:
        return {
            "message": f"Executed generic handler for {skill_name}.{tool_name}",
            "parameters": parameters,
            "success": True
        }
