# AetherCore Callable Skills Reference

## Overview

Callable skills are user-facing skills that can be invoked directly via the REST API. Core infrastructure skills (Orchestrator, EventMesh, OptiGraph) are internal-only.

## Callable Skills

### AetherCore.DeepForge
**Purpose**: Multi-phase research engine with evidence gathering

| Tool | Parameters | Returns |
|------|------------|---------|
| `research` | `query: string` | `{query, findings[], confidence}` |
| `analyze` | `data: object` | `{analysis, confidence}` |
| `verify` | `claim: string` | `{verification: boolean}` |
| `synthesize` | `sources: object[]` | `{synthesis: string}` |

**Aliases**: `deepforge`, `deep-forge`, `research`

---

### AetherCore.MarketSweep
**Purpose**: Marketplace scanning and deal comparison

| Tool | Parameters | Returns |
|------|------------|---------|
| `scan` | `query: string` | `{product, platforms_scanned}` |
| `compare` | `products: object[]` | `{lowest_price}` |
| `validate` | `deal: object` | `{valid: boolean}` |
| `score` | `deal: object` | `{deal_score: float}` |

**Aliases**: `marketsweep`, `market-sweep`, `commerce`, `deals`

---

### AetherCore.GeminiBridge
**Purpose**: Hybrid AI integration via Gemini API fallback

| Tool | Parameters | Returns |
|------|------------|---------|
| `escalate` | `prompt: string` | `{escalated, response}` |
| `crosscheck` | `data: object` | `{crosscheck, agreement: float}` |
| `debug` | `issue: string` | `{diagnostics}` |
| `alternatives` | `problem: string` | `{alternatives[]}` |

**Aliases**: `geminibridge`, `gemini-bridge`, `gemini`, `hybrid`

---

### AetherCore.PromptFoundry
**Purpose**: Dynamic prompt generation system

| Tool | Parameters | Returns |
|------|------------|---------|
| `generate` | `role: string` | `{role, prompt}` |
| `presets` | - | `{presets[]}` |
| `validate` | `prompt: string` | `{valid: boolean}` |
| `export` | `format: string` | `{format}` |

**Aliases**: `promptfoundry`, `prompt-foundry`, `prompts`, `factory`

---

## Common Response Fields

All skill outputs include:
- `_execution_time_ms`: Execution duration
- `_skill`: Canonical skill name
- `_tool`: Tool name executed
- `context_id`: Request tracking ID (when in orchestration)

### AetherCore.SearchEngine
**Purpose**: Multi-provider search with automatic failover and quota management

| Tool | Parameters | Returns |
|------|------------|---------|
| `search` | `query: string, max_results?: int, provider?: string` | `{provider, query, results[], quota_status}` |
| `scrape` | `url: string, render_js?: bool, use_premium_proxy?: bool` | `{provider, url, content, credits_used}` |
| `quota_status` | - | `{providers: {}, events[]}` |
| `reset_quotas` | `provider?: string` | `{success, quota_status}` |

**Providers**:
- Search: Google CSE (100/day), Brave (2000/mo), Serper (2000/mo)
- Scrape: Webscraping API (5000/mo), ScrapingAnt (10000 credits/mo)

**Aliases**: `searchengine`, `search-engine`, `search`, `websearch`

---

## API Usage

```bash
# Single tool execution
POST /tools/{skill_name}/{tool_name}
{
  "parameters": { ... },
  "context": { }
}

# Multi-skill orchestration
POST /orchestrate
{
  "workflow": [
    {"skill": "deepforge", "tool": "research", "params": {"query": "..."}},
    {"skill": "optigraph", "tool": "telemetry", "params": {}}
  ]
}
```
