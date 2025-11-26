# AetherCore.GeminiBridge v2.1 — Universal External Intelligence Engine

**Version:** 2.1  
**Classification:** External Intelligence Coprocessor  
**Author:** Tanner / ProjectGPT Ecosystem  
**Compatibility:** Universal Skill Integration Framework ≥1.0

-----

## Overview

AetherCore.GeminiBridge is a **universal external intelligence module** designed for the ProjectGPT FOIP ecosystem. Unlike traditional skills that target a single domain (research, code, product sourcing), Gemini-Hybrid operates as a **domain-general external cognition engine**.

Its purpose is to give ProjectGPT the ability to:

- Autonomously detect when internal reasoning is insufficient
- Escalate tasks to an external AI (Gemini API)
- Merge external insight with FOIP reasoning
- Produce a superior fused solution

AetherCore.GeminiBridge is not a research skill, not a code skill, not a product skill. It is a **cross-domain external coprocessor** used intelligently by ProjectGPT.

-----

## What Is AetherCore.GeminiBridge? (Purpose & Vision)

AetherCore.GeminiBridge is built to solve the systemic gaps of purely internal LLM workflows:

- Internal reasoning dead-ends
- Repeating code bugs the model can’t resolve
- Product searches with missing or incomplete results
- Logic chains that cannot converge
- Missing alternative perspectives
- Tasks that would benefit from independent model verification

It enables **multi-model cognition**, where ProjectGPT becomes the integrator and Gemini becomes a worker node.

-----

## Why This Skill Exists

Traditional skills handle narrow, predefined tasks. But ProjectGPT requires a subsystem that can dynamically decide:

- When to request external help
- Which parts of a task should be delegated
- How to merge external and internal reasoning
- When to override or refute external information
- When to escalate a repeated error
- How to maintain FOIP standards during fusion

AetherCore.GeminiBridge provides the missing layer: **adaptive delegation intelligence**.

-----

## Core Capabilities

### 4.1 Code-Centered Workflows

- Debug repeated errors
- Understand stack traces
- Rewrite full files or modules
- Produce alternative implementations
- Suggest architecture changes
- Provide expanded or stricter validations

### 4.2 Product Discovery

- Perform wide-net product search
- Find missing product candidates
- Return structured product data
- Feed results into DealFinder for filtering
- Merge results into a final, FOIP-verified output

### 4.3 Research & Knowledge Tasks

- Gather external evidence
- Provide counter-perspectives
- Identify contradictions
- Expand or validate ideas
- Provide long-form structured analysis

### 4.4 Logic, Planning, and Reasoning

- Generate alternative plans
- Provide systemic rewrites of thought paths
- Fill in missing inference steps
- Supply independent reasoning chains

**AetherCore.GeminiBridge is not tied to a domain** — it is a general-purpose augmentation engine.

-----

## Architecture Overview

AetherCore.GeminiBridge integrates into ProjectGPT via a four-layer architecture:

### 5.1 FOIP Delegation Ladder (FDL)

Defines when to delegate externally:

1. Internal reasoning attempt
1. User clarification attempt
1. External escalation via Gemini
1. Fusion and verification

### 5.2 External Delegation Logic (EDL)

Determines how to route tasks based on domain:

- `code` — debugging, implementation, architecture
- `products` — product search, comparison, data structuring
- `research` — evidence gathering, validation, synthesis
- `logic` — reasoning chains, planning, alternatives
- `fallback` — catch-all for undefined domains

### 5.3 Hybrid Fusion Engine (HFE)

Combines Gemini output with FOIP reasoning:

- Narrative merging
- Contradiction resolution
- Uncertainty mapping
- Detail expansion

### 5.4 Conflict Resolution System (CRS)

If FOIP and Gemini disagree:

- FOIP evaluates both
- Explains conflict
- Selects or merges the best elements
- Documents remaining uncertainty

-----

## Automatic Delegation Triggers

### 6.1 Code Escalation

**Triggered when:**

- The same error is reported twice
- Sequential patches fail
- Missing or unclear context prevents internal inference
- User indicates something “still doesn’t work”

### 6.2 Product Search Escalation

**Triggered when:**

- <5 products are found
- Mandatory specs not met
- Categories missing
- DealFinder cannot complete its mandate

### 6.3 Research Escalation

**Triggered when:**

- AetherCore.DeepForge cannot validate a claim
- Evidence conflict occurs
- Reasoning enters a loop
- Sources appear insufficient

### 6.4 Explicit Invocation

**Triggered by user phrases:**

- “Gemini, do this”
- “Ask Gemini”
- “Use Gemini for assistance”
- “Have Gemini work on it”
- “Cross-check with Gemini”

-----

## Delegation Modes

### 7.1 Internal → External → Fusion (Default)

FOIP attempts → Gemini augments → FOIP merges the result

### 7.2 Gemini-First Mode

Used when the user explicitly requests Gemini

### 7.3 Domain-Selective Delegation

Gemini is used only for specific domains: code, products, research, logic

### 7.4 Fallback Mode

If FOIP encounters a logic dead-end, repeated failures, or insufficient data, Gemini-Hybrid becomes the escalation route

-----

## Model Selection

### Gemini 2.0 Flash (Default)

**Use when:**

- Quick augmentation needed
- First attempt at escalation
- Normal depth requirements
- Cost efficiency prioritized

### Gemini 2.5 Pro (Advanced)

**Use when:**

- Attempts ≥ 2
- Contradictions detected
- Depth hint = “deep”
- Task type ∈ {code, research, logic} AND internal attempts failed
- High-stakes reasoning required

The **AetherCore.OptiGraph and AetherCore.Orchestrator** automatically select the appropriate model based on task context and failure patterns.

-----

## Input/Output Structure

### Input Format

```json
{
  "task": "<string>",
  "context": {
    "task_type": "code|products|research|logic|fallback",
    "attempts": 1,
    "flags": {},
    "skill_outputs": {}
  },
  "domain": "code",
  "depth": "brief|normal|deep",
  "api_key": "<string>"
}
```

### Output Format (Success)

```json
{
  "status": "ok",
  "origin": "gemini_hybrid",
  "evidence": "<external long-form text>",
  "metadata": {
    "model_used": "gemini-2.0-flash",
    "tokens_used": 1234,
    "timestamp": 1234567890,
    "response_time_ms": 850
  }
}
```

### Output Format (Error)

```json
{
  "status": "error",
  "origin": "gemini_hybrid",
  "error": "Error description",
  "timestamp": 1234567890
}
```

-----

## FOIP Integration

### FOIP External Delegation Ruleset (FOIP-EDR)

Controls:

- Escalation detection
- Fallback routing
- Structured rewrites
- Uncertainty propagation
- Multi-model merging

### FOIP Continuation Layer

Ensures:

- Format consistency
- Continuation rules (”(continued...)”)
- Structural inheritance
- Tone enforcement

### FOIP Fusion Protocol

Defines how Gemini’s results are:

- Critiqued
- Validated
- Corrected
- Merged
- Finalized

-----

## File Structure

```
AetherCore/GeminiBridge/
├── geminibridge-geminibridge-config.json # Skill configuration
├── gemini-hybrid.md         # Skill definition & rules
├── GeminiBridge-client.js   # API client implementation
└── README.md                # This file
```

-----

## Installation & Auto-Bootstrap

### Step 1: Structure

AetherCore.GeminiBridge is located in ProjectGPT’s `AetherCore/` directory:

```
AetherCore/
└── GeminiBridge/
    ├── geminibridge-config.json
    ├── gemini-hybrid.md
    ├── GeminiBridge-client.js
    └── README.md
```

### Step 2: Auto-Registration

FOIP + USIF will:

1. Detect `geminibridge-geminibridge-config.json`
1. Register the skill
1. Assign default priority
1. Enable AetherCore.GeminiBridge for delegation pathways

### Step 3: Verification

You will see logs indicating:

```
✓ Registered skill: AetherCore.GeminiBridge
AetherCore.GeminiBridge delegation engine active
```

-----

## Usage Examples

### Example 1 — Code Escalation

```
User: "It still errors..."

→ FOIP detects repeated failure
→ AetherCore.GeminiBridge is invoked
→ Gemini proposes a patch
→ FOIP critiques and merges
→ Final output delivered
```

### Example 2 — Product Search Fallback

```
→ AetherCore.MarketSweep finds <5 products
→ Gemini searches wide-net
→ AetherCore.MarketSweep filters
→ FOIP merges
→ Final comparison returned
```

### Example 3 — Hybrid Research

```
→ AetherCore.DeepForge stuck on contradictory evidence
→ AetherCore.GeminiBridge runs external pass
→ FOIP resolves contradictions
→ Unified long-form answer produced
```

### Example 4 — Direct Invocation

```
User: "Gemini, rewrite this function."

→ Skill routes command
→ Gemini provides rewrite
→ FOIP verifies
→ Output returned
```

-----

## Limitations

- Requires a valid Gemini API key
- Requires host internet access
- FOIP always remains the final reasoning layer
- External model output is never accepted blindly
- No long-term external state persistence

-----

## Roadmap

**Planned Features:**

- Multi-model parallel fusion (Gemini + others)
- Probabilistic fusion weighting
- Dynamic model selector
- Cross-checking external models against each other
- Multi-phase delegated pipelines
- Tertiary fallback engines (Claude, GPT-4, etc.)

-----

## Support & Troubleshooting

### Common Issues

**Issue:** “Missing Gemini API key”  
**Solution:** Ensure API key is provided in runtime environment or payload

**Issue:** “Model not found”  
**Solution:** Verify model name is either `gemini-2.0-flash` or `gemini-2.5-pro`

**Issue:** “Empty Gemini response”  
**Solution:** Check prompt formatting and API quota limits

**Issue:** “Skill not registered”  
**Solution:** Verify file structure matches expected layout in `AetherCore/GeminiBridge/`

-----

## Configuration Reference

See `geminibridge-config.json` for full configuration options including:

- Model selection heuristics
- Escalation triggers
- Event subscriptions
- Routing handlers
- Output contracts

-----

## License & Terms

This module must comply with:

- ProjectGPT usage policies
- FOIP system constraints
- Gemini API usage and safety guidelines

-----

## Status

✅ **Production Ready** (v2.1)

**Tested With:**

- AetherCore.Orchestrator v2.0
- AetherCore.EventMesh v1.1
- AetherCore.OptiGraph v1.0
- AetherCore.DeepForge v1.0
- AetherCore.MarketSweep v1.0

**Known Issues:** None

-----

**Last Updated:** November 13, 2025  
**Maintainer:** ProjectGPT Core Team  
**Support:** Check ProjectGPT system documentation or runtime logs

-----

**End of README**
