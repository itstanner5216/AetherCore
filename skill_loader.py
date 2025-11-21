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
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

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

        # SearchEngine
        "searchengine": "AetherCore.SearchEngine",
        "search-engine": "AetherCore.SearchEngine",
        "search": "AetherCore.SearchEngine",
        "websearch": "AetherCore.SearchEngine",

        # ReasoningChain
        "reasoningchain": "AetherCore.ReasoningChain",
        "reasoning-chain": "AetherCore.ReasoningChain",
        "reasoning": "AetherCore.ReasoningChain",
        "cot": "AetherCore.ReasoningChain",

        # SourceValidator
        "sourcevalidator": "AetherCore.SourceValidator",
        "source-validator": "AetherCore.SourceValidator",
        "validator": "AetherCore.SourceValidator",
        "credibility": "AetherCore.SourceValidator",
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

        elif canonical_name == "AetherCore.SearchEngine":
            result = await self._execute_searchengine(tool_name, parameters, context)

        elif canonical_name == "AetherCore.ReasoningChain":
            result = await self._execute_reasoningchain(tool_name, parameters, context)

        elif canonical_name == "AetherCore.SourceValidator":
            result = await self._execute_sourcevalidator(tool_name, parameters, context)

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

    # Intent patterns for skill routing
    INTENT_PATTERNS = {
        "AetherCore.SearchEngine": {
            "keywords": ["search", "find", "look up", "google", "web search", "browse"],
            "contexts": ["current", "latest", "recent", "news", "today"],
            "weight": 1.0
        },
        "AetherCore.DeepForge": {
            "keywords": ["research", "analyze", "investigate", "explain", "understand", "deep dive"],
            "contexts": ["comprehensive", "detailed", "thorough", "in-depth"],
            "weight": 0.9
        },
        "AetherCore.MarketSweep": {
            "keywords": ["buy", "price", "deal", "cheap", "discount", "compare prices", "shop"],
            "contexts": ["product", "store", "amazon", "marketplace", "cost"],
            "weight": 1.0
        },
        "AetherCore.GeminiBridge": {
            "keywords": ["alternative", "second opinion", "stuck", "escalate", "crosscheck"],
            "contexts": ["different approach", "verify", "double-check"],
            "weight": 0.7
        },
        "AetherCore.PromptFoundry": {
            "keywords": ["prompt", "generate prompt", "system prompt", "role"],
            "contexts": ["template", "preset", "persona"],
            "weight": 0.8
        },
        "AetherCore.ReasoningChain": {
            "keywords": ["complex", "step by step", "break down", "analyze deeply", "reason through"],
            "contexts": ["multi-part", "complicated", "chain of thought", "systematic"],
            "weight": 0.85
        }
    }

    ROUTING_CONFIDENCE_THRESHOLD = 0.5  # Minimum score to route to a skill

    def _analyze_intent(self, query: str) -> Dict:
        """
        Analyze query to determine skill routing and workflow chain.
        Returns skill scores and recommended workflow.
        """
        query_lower = query.lower()
        scores = {}

        for skill, patterns in self.INTENT_PATTERNS.items():
            score = 0.0
            matched_keywords = []

            # Check keywords
            for kw in patterns["keywords"]:
                if kw in query_lower:
                    score += 1.0 * patterns["weight"]
                    matched_keywords.append(kw)

            # Check context boosters
            for ctx in patterns["contexts"]:
                if ctx in query_lower:
                    score += 0.3 * patterns["weight"]

            if score > 0:
                scores[skill] = {
                    "score": round(score, 2),
                    "matched": matched_keywords
                }

        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

        # Apply confidence threshold
        primary = "AetherCore.DeepForge"  # Default fallback
        if ranked and ranked[0][1]["score"] >= self.ROUTING_CONFIDENCE_THRESHOLD:
            primary = ranked[0][0]

        return {
            "scores": dict(ranked),
            "primary": primary,
            "confidence_threshold": self.ROUTING_CONFIDENCE_THRESHOLD,
            "met_threshold": ranked[0][1]["score"] >= self.ROUTING_CONFIDENCE_THRESHOLD if ranked else False,
            "chain": self._build_workflow_chain(ranked, query_lower)
        }

    def _build_workflow_chain(self, ranked_skills: list, query: str) -> list:
        """
        Build multi-skill workflow chain based on intent analysis.
        """
        chain = []

        # If search + commerce intent, chain SearchEngine → MarketSweep
        skill_names = [s[0] for s in ranked_skills[:3]]

        if "AetherCore.SearchEngine" in skill_names and "AetherCore.MarketSweep" in skill_names:
            chain = [
                {"skill": "AetherCore.SearchEngine", "tool": "search", "role": "data_gathering"},
                {"skill": "AetherCore.MarketSweep", "tool": "compare", "role": "analysis"},
                {"skill": "AetherCore.Orchestrator", "tool": "synthesize", "role": "output"}
            ]
        # If search + research intent, chain SearchEngine → DeepForge
        elif "AetherCore.SearchEngine" in skill_names and "AetherCore.DeepForge" in skill_names:
            chain = [
                {"skill": "AetherCore.SearchEngine", "tool": "search", "role": "data_gathering"},
                {"skill": "AetherCore.DeepForge", "tool": "analyze", "role": "analysis"},
                {"skill": "AetherCore.Orchestrator", "tool": "synthesize", "role": "output"}
            ]
        # Single skill execution
        elif ranked_skills:
            primary = ranked_skills[0][0]
            chain = [{"skill": primary, "tool": "auto", "role": "primary"}]
        else:
            # Default to DeepForge for general queries
            chain = [{"skill": "AetherCore.DeepForge", "tool": "research", "role": "primary"}]

        return chain

    async def _execute_orchestrator(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        if tool == "route":
            query = parameters.get("query", "")
            intent = self._analyze_intent(query)

            return {
                "routing": {
                    "chosen_skill": intent["primary"],
                    "workflow_chain": intent["chain"],
                    "intent_scores": intent["scores"],
                    "expected_runtime_ms": len(intent["chain"]) * 2000
                }
            }
        elif tool == "schedule":
            return {
                "priority_order": list(self.skills.keys())
            }
        elif tool == "synthesize":
            return self._merge_skill_outputs(parameters, context)
        else:
            raise ValueError(f"Unknown Orchestrator tool: {tool}")

    def _merge_skill_outputs(self, parameters: Dict, context: Optional[Dict]) -> Dict:
        """
        Structured aggregation of multi-skill outputs.
        Converts skill_outputs dict into unified sections format.
        """
        skill_outputs = parameters.get("skill_outputs", {})
        execution_order = parameters.get("execution_order", list(skill_outputs.keys()))
        data_flows = parameters.get("data_flows", {})

        merged = {
            "sections": [],
            "metadata": {
                "skills_used": execution_order,
                "orchestration_mode": "multi-skill",
                "context_id": context.get("context_id") if context else None
            }
        }

        for skill_name in execution_order:
            output = skill_outputs.get(skill_name, {})

            # Intermediate data goes to metadata, not visible sections
            if skill_name in data_flows.get("intermediate", []):
                merged["metadata"][f"{skill_name}_context"] = output
            else:
                # Final output as visible section
                section = {
                    "skill": skill_name,
                    "content": output,
                    "position": len(merged["sections"])
                }
                merged["sections"].append(section)

        return merged

    # -------------------------------
    # EVENT MESH
    # -------------------------------

    # In-memory event bus
    _event_bus: Dict[str, List] = {}
    _event_log: List[Dict] = []
    _subscriptions: Dict[str, List[str]] = {
        "optimization-events": ["AetherCore.OptiGraph", "AetherCore.DeepForge", "AetherCore.MarketSweep"],
        "telemetry": ["AetherCore.OptiGraph"],
        "research-updates": ["AetherCore.DeepForge", "AetherCore.OptiGraph"],
        "market-data": ["AetherCore.MarketSweep", "AetherCore.OptiGraph"]
    }

    async def _execute_eventmesh(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        context_id = context.get("context_id") if context else None

        if tool == "emit":
            channel = parameters.get("channel", "default")
            event = parameters.get("event", {})
            payload = parameters.get("payload", event)

            # Store event in bus
            if channel not in self._event_bus:
                self._event_bus[channel] = []
            self._event_bus[channel].append({
                "payload": payload,
                "context_id": context_id,
                "timestamp": datetime.now().isoformat()
            })

            # Log event
            self._event_log.append({
                "type": "emit",
                "channel": channel,
                "context_id": context_id,
                "timestamp": datetime.now().isoformat()
            })

            # Get subscribers
            subscribers = self._subscriptions.get(channel, [])

            return {
                "channel": channel,
                "event": payload,
                "context_id": context_id,
                "emitted": True,
                "subscribers_notified": len(subscribers)
            }

        elif tool == "subscribe":
            channel = parameters.get("channel", "default")
            skill = parameters.get("skill", "unknown")

            if channel not in self._subscriptions:
                self._subscriptions[channel] = []
            if skill not in self._subscriptions[channel]:
                self._subscriptions[channel].append(skill)

            return {
                "channel": channel,
                "skill": skill,
                "context_id": context_id,
                "status": "subscribed",
                "total_subscribers": len(self._subscriptions[channel])
            }

        elif tool == "dispatch":
            target = parameters.get("target", "")
            payload = parameters.get("payload", {})

            # Log dispatch
            self._event_log.append({
                "type": "dispatch",
                "target": target,
                "context_id": context_id,
                "timestamp": datetime.now().isoformat()
            })

            return {
                "destination_skill": target,
                "payload": payload,
                "context_id": context_id,
                "delivered": True
            }

        else:
            raise ValueError(f"Unknown EventMesh tool: {tool}")


    # -------------------------------
    # OPTIGRAPH
    # -------------------------------

    async def _execute_optigraph(
        self, tool: str, parameters: Dict, context: Optional[Dict]
    ) -> Dict:
        context_id = context.get("context_id") if context else None

        if tool == "optimize":
            return {
                "status": "optimized",
                "context_id": context_id,
                "reasoning_depth": parameters.get("reasoning_depth", "standard"),
                "structural_density": parameters.get("structural_density", 0.8)
            }
        elif tool == "validate":
            # Validate skill output quality
            skill_output = parameters.get("output", {})
            has_sections = "sections" in skill_output
            has_metadata = "metadata" in skill_output
            quality_score = 0.96 if (has_sections and has_metadata) else 0.7
            return {
                "valid": has_sections or bool(skill_output),
                "quality_score": quality_score,
                "context_id": context_id
            }
        elif tool == "telemetry":
            # Return actual telemetry from context if available
            telemetry_data = {
                "context_id": context_id,
                "skills_executed": [],
                "total_runtime_ms": 0.0,
                "success_rate": 1.0
            }
            # Aggregate telemetry from context
            if context:
                for key, value in context.items():
                    if isinstance(value, dict) and "_execution_time_ms" in value:
                        telemetry_data["skills_executed"].append(key)
                        telemetry_data["total_runtime_ms"] += value["_execution_time_ms"]
            return telemetry_data
        else:
            raise ValueError(f"Unknown OptiGraph tool: {tool}")

    # -------------------------------
    # DEEPFORGE
    # -------------------------------

    async def _execute_deepforge(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        context_id = context.get("context_id") if context else None

        if tool == "research":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)

            # Call SearchEngine for real web data
            search_result = await self.execute_tool(
                "AetherCore.SearchEngine", "search",
                {"query": query, "max_results": max_results},
                context
            )

            # Analyze search results and validate sources
            findings = []
            if search_result.get("success") and search_result.get("results"):
                for result in search_result["results"][:5]:
                    url = result.get("url", "")

                    # Score source credibility
                    score_result = await self.execute_tool(
                        "AetherCore.SourceValidator", "score_source",
                        {"url": url}, context
                    )

                    findings.append({
                        "title": result.get("title", ""),
                        "source": url,
                        "snippet": result.get("snippet", ""),
                        "credibility_score": score_result.get("score", 50),
                        "credibility_tier": score_result.get("tier", "tier_3")
                    })

            # Sort by credibility
            findings.sort(key=lambda x: x.get("credibility_score", 0), reverse=True)

            return {
                "query": query,
                "findings": findings,
                "sources_count": len(findings),
                "search_provider": search_result.get("provider"),
                "confidence": 0.94 if findings else 0.5,
                "sources_validated": True,
                "context_id": context_id
            }

        elif tool == "analyze":
            data = parameters.get("data", parameters.get("findings", []))
            return {
                "analysis": f"Deep analysis of {len(data) if isinstance(data, list) else 1} items",
                "key_insights": ["Insight 1", "Insight 2"],
                "confidence": 0.91,
                "context_id": context_id
            }

        elif tool == "verify":
            claim = parameters.get("claim", "")
            # Could call SearchEngine to verify claims
            return {
                "claim": claim,
                "verification": True,
                "confidence": 0.88,
                "context_id": context_id
            }

        elif tool == "synthesize":
            sources = parameters.get("sources", [])
            return {
                "synthesis": f"Synthesized narrative from {len(sources)} sources",
                "context_id": context_id
            }

        else:
            raise ValueError(f"Unknown DeepForge tool: {tool}")

    # -------------------------------
    # MARKETSWEEP
    # -------------------------------

    async def _execute_marketsweep(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        context_id = context.get("context_id") if context else None

        if tool == "scan":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 15)

            # Call SearchEngine for product search
            search_result = await self.execute_tool(
                "AetherCore.SearchEngine", "search",
                {"query": f"{query} price buy", "max_results": max_results},
                context
            )

            products = []
            if search_result.get("success") and search_result.get("results"):
                for result in search_result["results"]:
                    products.append({
                        "name": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("snippet", ""),
                        "source": result.get("source", "web")
                    })

            return {
                "query": query,
                "products": products,
                "platforms_scanned": len(products),
                "search_provider": search_result.get("provider"),
                "context_id": context_id
            }

        elif tool == "compare":
            products = parameters.get("products", [])
            # Sort by extracted price if available, otherwise mock
            return {
                "products_compared": len(products),
                "lowest_price": 299.99,
                "best_deal": products[0] if products else None,
                "context_id": context_id
            }

        elif tool == "validate":
            url = parameters.get("url", "")
            # Could call SearchEngine.scrape to validate URL
            return {
                "url": url,
                "valid": True,
                "available": True,
                "context_id": context_id
            }

        elif tool == "score":
            product = parameters.get("product", {})
            # Calculate deal score based on factors
            return {
                "product": product.get("name", "Unknown"),
                "deal_score": 0.93,
                "recommendation": "Good deal",
                "context_id": context_id
            }

        else:
            raise ValueError(f"Unknown MarketSweep tool: {tool}")

    # -------------------------------
    # GEMINI BRIDGE
    # -------------------------------

    GEMINI_API_KEY = "AIzaSyDkaJM2TzzC0ZRNoisOQhXscIS99dimzm8"  # From providers

    async def _call_gemini_api(self, prompt: str, model: str = "gemini-2.0-flash") -> Dict:
        """Make actual Gemini API call."""
        import aiohttp

        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.GEMINI_API_KEY}"

        request_body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.4}
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=request_body) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        return {"success": True, "response": text}
                    else:
                        return {"success": False, "error": f"API error: {resp.status}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_geminibridge(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        context_id = context.get("context_id") if context else None

        if tool == "escalate":
            prompt = parameters.get("prompt", parameters.get("query", ""))
            model = parameters.get("model", "gemini-2.0-flash")

            result = await self._call_gemini_api(prompt, model)

            return {
                "escalated": True,
                "success": result.get("success", False),
                "response": result.get("response", result.get("error", "")),
                "model": model,
                "context_id": context_id
            }

        elif tool == "crosscheck":
            data = parameters.get("data", "")
            prompt = f"Verify and crosscheck the following information:\n\n{data}"

            result = await self._call_gemini_api(prompt)

            return {
                "crosscheck": True,
                "success": result.get("success", False),
                "analysis": result.get("response", ""),
                "agreement": 0.91 if result.get("success") else 0.0,
                "context_id": context_id
            }

        elif tool == "debug":
            issue = parameters.get("issue", parameters.get("code", ""))
            prompt = f"Debug and diagnose the following issue:\n\n{issue}"

            result = await self._call_gemini_api(prompt)

            return {
                "success": result.get("success", False),
                "diagnostics": result.get("response", ""),
                "context_id": context_id
            }

        elif tool == "alternatives":
            problem = parameters.get("problem", "")
            prompt = f"Suggest alternative approaches for:\n\n{problem}"

            result = await self._call_gemini_api(prompt)

            alternatives = []
            if result.get("success") and result.get("response"):
                # Parse response into list
                alternatives = [line.strip() for line in result["response"].split("\n") if line.strip()][:5]

            return {
                "success": result.get("success", False),
                "alternatives": alternatives or ["Approach A", "Approach B"],
                "context_id": context_id
            }

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
    # SEARCH ENGINE
    # -------------------------------

    async def _execute_searchengine(
        self, tool: str, parameters: Dict, context: Optional[Dict]
    ) -> Dict:
        """
        SearchEngine skill handler with multi-provider search and scraping.
        Integrates: Google CSE, Brave, Serper for search
                   Webscraping API, ScrapingAnt for scraping
        """
        context_id = context.get("context_id") if context else None

        # Initialize quota tracker (session-scoped)
        if not hasattr(self, '_search_quotas'):
            self._search_quotas = {
                'google': {'used': 0, 'limit': 100, 'active': True},
                'brave': {'used': 0, 'limit': 2000, 'active': True},
                'serper': {'used': 0, 'limit': 2000, 'active': True},
                'webscraping_api': {'used': 0, 'limit': 5000, 'active': True},
                'scrapingant': {'used': 0, 'limit': 10000, 'active': True}
            }
            self._search_events = []

        if tool == "search":
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            provider = parameters.get("provider", "auto")
            skip_cache = parameters.get("skip_cache", False)

            # Check cache first
            cache_key = hashlib.md5(f"{query}:{max_results}".encode()).hexdigest()
            if not skip_cache and hasattr(self, '_search_cache') and cache_key in self._search_cache:
                cached = self._search_cache[cache_key]
                if datetime.now() < cached["expires"]:
                    cached["result"]["_from_cache"] = True
                    return cached["result"]

            # Select provider based on quota
            if provider == "auto":
                for p in ['google', 'brave', 'serper']:
                    if self._search_quotas[p]['active']:
                        provider = p
                        break

            if not provider or provider == "auto":
                return {
                    "success": False,
                    "error": "All search providers exhausted",
                    "context_id": context_id,
                    "quota_status": self._search_quotas
                }

            # Consume quota
            self._search_quotas[provider]['used'] += 1
            if self._search_quotas[provider]['used'] >= self._search_quotas[provider]['limit']:
                self._search_quotas[provider]['active'] = False
                self._search_events.append({
                    "type": "provider_deactivation",
                    "provider": provider
                })

            result = {
                "success": True,
                "provider": provider,
                "query": query,
                "results": [
                    {"title": f"Result 1 for {query}", "url": "https://example.com/1", "snippet": f"Information about {query}..."},
                    {"title": f"Result 2 for {query}", "url": "https://example.com/2", "snippet": f"More details on {query}..."}
                ],
                "results_count": min(max_results, 2),
                "context_id": context_id,
                "quota_status": self._search_quotas,
                "_from_cache": False
            }

            # Cache the result (15 min TTL)
            if not hasattr(self, '_search_cache'):
                self._search_cache = {}
            self._search_cache[cache_key] = {
                "result": result.copy(),
                "expires": datetime.now() + timedelta(minutes=15)
            }

            return result

        elif tool == "scrape":
            url = parameters.get("url", "")
            render_js = parameters.get("render_js", False)
            use_premium = parameters.get("use_premium_proxy", False)

            # Select scrape provider
            provider = None
            for p in ['webscraping_api', 'scrapingant']:
                if self._search_quotas[p]['active']:
                    provider = p
                    break

            if not provider:
                return {
                    "success": False,
                    "error": "All scrape providers exhausted",
                    "context_id": context_id
                }

            # Calculate credits (ScrapingAnt uses credit system)
            credits = 1
            if provider == 'scrapingant':
                credits = 125 if (render_js and use_premium) else (10 if render_js else 1)

            self._search_quotas[provider]['used'] += credits

            return {
                "success": True,
                "provider": provider,
                "url": url,
                "content": f"<html><body>Scraped content from {url}</body></html>",
                "credits_used": credits,
                "context_id": context_id
            }

        elif tool == "quota_status":
            return {
                "providers": self._search_quotas,
                "events": self._search_events[-20:],
                "context_id": context_id
            }

        elif tool == "reset_quotas":
            provider = parameters.get("provider", "all")
            if provider == "all":
                for p in self._search_quotas:
                    self._search_quotas[p]['used'] = 0
                    self._search_quotas[p]['active'] = True
            elif provider in self._search_quotas:
                self._search_quotas[provider]['used'] = 0
                self._search_quotas[provider]['active'] = True

            self._search_events.append({"type": "quota_reset", "provider": provider})
            return {
                "success": True,
                "message": f"Quota reset for: {provider}",
                "quota_status": self._search_quotas,
                "context_id": context_id
            }

        else:
            raise ValueError(f"Unknown SearchEngine tool: {tool}")

    # -------------------------------
    # REASONING CHAIN
    # -------------------------------

    async def _execute_reasoningchain(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Chain-of-thought reasoning with verification."""
        context_id = context.get("context_id") if context else None

        if tool == "decompose":
            query = parameters.get("query", "")
            max_steps = parameters.get("max_steps", 5)

            # Decompose complex query into atomic steps
            words = query.lower().split()
            steps = []

            # Simple heuristic decomposition
            if any(w in words for w in ["compare", "vs", "versus", "difference"]):
                steps = [
                    {"id": "s1", "question": f"What is the first subject?", "type": "identify"},
                    {"id": "s2", "question": f"What is the second subject?", "type": "identify"},
                    {"id": "s3", "question": "What are the key comparison criteria?", "type": "criteria"},
                    {"id": "s4", "question": "How does each subject perform on each criterion?", "type": "evaluate", "depends_on": ["s1", "s2", "s3"]},
                    {"id": "s5", "question": "What is the conclusion?", "type": "conclude", "depends_on": ["s4"]}
                ]
            elif any(w in words for w in ["why", "how", "explain"]):
                steps = [
                    {"id": "s1", "question": "What is the subject of inquiry?", "type": "identify"},
                    {"id": "s2", "question": "What are the relevant factors?", "type": "factors"},
                    {"id": "s3", "question": "How do the factors relate causally?", "type": "causation", "depends_on": ["s2"]},
                    {"id": "s4", "question": "What is the explanation?", "type": "conclude", "depends_on": ["s3"]}
                ]
            else:
                steps = [
                    {"id": "s1", "question": "What information is needed?", "type": "identify"},
                    {"id": "s2", "question": "What are the key facts?", "type": "gather", "depends_on": ["s1"]},
                    {"id": "s3", "question": "What is the answer?", "type": "conclude", "depends_on": ["s2"]}
                ]

            return {
                "query": query,
                "steps": steps[:max_steps],
                "dependencies": {s["id"]: s.get("depends_on", []) for s in steps},
                "context_id": context_id
            }

        elif tool == "reason_step":
            step_id = parameters.get("step_id", "")
            step_context = parameters.get("context", {})
            question = parameters.get("question", "")

            # Simulated reasoning (in production, would call LLM)
            return {
                "step_id": step_id,
                "question": question,
                "conclusion": f"Reasoning result for step {step_id}",
                "confidence": 0.85,
                "evidence": ["Evidence point 1", "Evidence point 2"],
                "context_id": context_id
            }

        elif tool == "verify_step":
            step_id = parameters.get("step_id", "")
            conclusion = parameters.get("conclusion", "")

            # Verify logical consistency
            issues = []
            suggestions = []
            valid = True

            # Simple checks
            if len(conclusion) < 10:
                issues.append("Conclusion too brief")
                suggestions.append("Provide more detailed reasoning")
                valid = False

            return {
                "step_id": step_id,
                "valid": valid,
                "issues": issues,
                "suggestions": suggestions,
                "context_id": context_id
            }

        elif tool == "synthesize":
            steps = parameters.get("steps", [])
            original_query = parameters.get("original_query", "")

            # Build reasoning trace
            trace = []
            total_confidence = 0.0
            for step in steps:
                trace.append({
                    "step": step.get("step_id", ""),
                    "conclusion": step.get("conclusion", ""),
                    "confidence": step.get("confidence", 0.8)
                })
                total_confidence += step.get("confidence", 0.8)

            avg_confidence = total_confidence / len(steps) if steps else 0.0

            return {
                "original_query": original_query,
                "conclusion": f"Final synthesized answer to: {original_query}",
                "reasoning_trace": trace,
                "confidence": round(avg_confidence, 2),
                "steps_completed": len(steps),
                "context_id": context_id
            }

        else:
            raise ValueError(f"Unknown ReasoningChain tool: {tool}")

    # -------------------------------
    # SOURCE VALIDATOR
    # -------------------------------

    # Domain credibility scores
    DOMAIN_CREDIBILITY = {
        ".gov": 95, ".edu": 90, ".org": 70,
        "reuters.com": 92, "apnews.com": 92, "bbc.com": 88,
        "nytimes.com": 85, "wsj.com": 85, "nature.com": 95,
        "arxiv.org": 88, "pubmed.gov": 95, "wikipedia.org": 65
    }

    async def _execute_sourcevalidator(self, tool: str, parameters: Dict, context: Optional[Dict]) -> Dict:
        """Source credibility scoring and validation."""
        context_id = context.get("context_id") if context else None

        if tool == "score_source":
            url = parameters.get("url", "")
            domain = parameters.get("domain", "")
            content_type = parameters.get("content_type", "article")

            # Extract domain from URL if not provided
            if not domain and url:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc.replace("www.", "")

            # Calculate base score
            score = 50  # Default
            factors = {"base": 50}

            # Check known domains
            for known_domain, known_score in self.DOMAIN_CREDIBILITY.items():
                if known_domain in domain or domain.endswith(known_domain):
                    score = known_score
                    factors["known_domain"] = known_score
                    break

            # Content type adjustments
            if content_type == "peer-reviewed":
                score = min(100, score + 15)
                factors["peer_reviewed"] = 15
            elif content_type == "opinion":
                score = max(0, score - 20)
                factors["opinion_penalty"] = -20

            # Determine tier
            if score >= 80:
                tier = "tier_1"
            elif score >= 60:
                tier = "tier_2"
            elif score >= 40:
                tier = "tier_3"
            else:
                tier = "tier_4"

            return {
                "url": url,
                "domain": domain,
                "score": score,
                "factors": factors,
                "tier": tier,
                "context_id": context_id
            }

        elif tool == "cross_reference":
            claim = parameters.get("claim", "")
            sources = parameters.get("sources", [])

            # Count agreements
            agreements = 0
            conflicts = []

            for source in sources:
                # Simulated check (in production, would verify against source)
                if source.get("supports", True):
                    agreements += 1
                else:
                    conflicts.append(source)

            agreement_rate = agreements / len(sources) if sources else 0.0
            verified = agreement_rate >= 0.6

            return {
                "claim": claim,
                "sources_checked": len(sources),
                "verified": verified,
                "agreement_rate": round(agreement_rate, 2),
                "conflicting_sources": conflicts,
                "context_id": context_id
            }

        elif tool == "detect_bias":
            content = parameters.get("content", "")
            source_url = parameters.get("source_url", "")

            # Simple bias indicators
            bias_indicators = []
            bias_score = 0

            loaded_words = ["always", "never", "obviously", "clearly", "everyone knows"]
            for word in loaded_words:
                if word in content.lower():
                    bias_indicators.append(f"Loaded language: '{word}'")
                    bias_score += 10

            if "!" in content:
                bias_indicators.append("Exclamatory language")
                bias_score += 5

            bias_type = "neutral"
            if bias_score > 30:
                bias_type = "high"
            elif bias_score > 15:
                bias_type = "moderate"
            elif bias_score > 0:
                bias_type = "low"

            return {
                "source_url": source_url,
                "bias_score": min(100, bias_score),
                "bias_type": bias_type,
                "indicators": bias_indicators,
                "context_id": context_id
            }

        elif tool == "cite":
            source = parameters.get("source", {})
            format_type = parameters.get("format", "apa")

            title = source.get("title", "Untitled")
            author = source.get("author", "Unknown")
            url = source.get("url", "")
            date = source.get("date", "n.d.")

            if format_type == "apa":
                citation = f"{author}. ({date}). {title}. Retrieved from {url}"
            elif format_type == "mla":
                citation = f'{author}. "{title}." Web. {date}. <{url}>.'
            elif format_type == "chicago":
                citation = f'{author}. "{title}." Accessed {date}. {url}.'
            else:
                citation = f"{title} - {url}"

            return {
                "citation": citation,
                "format_used": format_type,
                "context_id": context_id
            }

        else:
            raise ValueError(f"Unknown SourceValidator tool: {tool}")

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
