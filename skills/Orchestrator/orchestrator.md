---
name: "AetherCore.Orchestrator"
description: Root executive controller that governs skill taxonomy, activation sequences, and multi-skill orchestration across the AetherCore ecosystem.
version: 2.0
type: core-controller
entry_point: orchestrator-entry.js
execution_priority: 0
auto_initialize: true
---

# AetherCore.Orchestrator v2.0 — Root Executive Controller

## System Architecture Role

**AetherCore.Orchestrator is the ROOT CONTROLLER of the AetherCore system.**

This skill initializes FIRST in every session, before any other module executes. It defines the complete skill ecosystem, establishes execution sequences, manages dependencies, and orchestrates multi-skill workflows.

**Critical Directive**: This controller ALWAYS activates automatically at session start, regardless of user input.

---

## Skill Taxonomy & Classification System

The Orchestrator maintains a strict two-tier classification of all modules:

### Tier 1: Non-Callable Core Modules

These modules are **infrastructure components** that activate automatically in a fixed sequence. They are NEVER user-invoked and operate transparently.

| Module | Role | Activation Rule |
|:---|:---|:---|
| **AetherCore.Orchestrator** | Root Controller | Always first; initializes environment |
| **AetherCore.EventMesh** | Event Routing Infrastructure | Auto-instantiated by Orchestrator |
| **AetherCore.OptiGraph** | Policy & Parameter Tuning | Auto-activated after Graph |

**Execution Order (Mandatory)**:
```
AetherCore.Orchestrator → AetherCore.EventMesh → AetherCore.OptiGraph
```

This sequence MUST complete before any callable skill executes.

### Tier 2: Callable Skills

These are **functional capabilities** invoked on demand based on user intent:

| Skill | Purpose | Invocation Type |
|:---|:---|:---|
| **AetherCore.DeepForge** | Multi-phase research with source validation | Explicit or contextual |
| **AetherCore.PromptFoundry** | Role-specific mega-prompt generation | Explicit or contextual |
| **AetherCore.MarketSweep** | Product comparison with validated purchase links | Explicit or contextual |

**Invocation Rules**:
- Single skill reference → Execute that skill in isolation
- Multiple skill references → Orchestrate dependencies and merge outputs
- No explicit skill reference → Infer from context (default: research or prompt generation)

---

## Core Activation Sequence (Automatic)

On every session initialization, the following sequence executes silently:

### Phase 1: Environment Bootstrap
```python
def initialize_environment():
    """
    Root controller initialization - always runs first
    """
    # Step 1: Load skill registry
    registry = load_all_skills()
    
    # Step 2: Classify skills by tier
    core_modules = classify_core_modules(registry)
    callable_skills = classify_callable_skills(registry)
    
    # Step 3: Store taxonomy in session state
    session_state.core_modules = core_modules
    session_state.callable_skills = callable_skills
    session_state.orchestrator_active = True
    
    return {
        "status": "orchestrator_initialized",
        "core_modules": len(core_modules),
        "callable_skills": len(callable_skills)
    }
```

### Phase 2: Infrastructure Instantiation
```python
def instantiate_infrastructure():
    """
    Create Automation Graph and activate Optimization Profile
    """
    # Step 1: Initialize Automation Graph
    graph = automation_graph.on_registry_init(session_state.registry)
    
    # Step 2: Build routing tables
    graph.build_routing_table(session_state.core_modules + session_state.callable_skills)
    
    # Step 3: Activate Optimization Profile
    optimization_profile.optimize_registry()
    
    # Step 4: Register event handlers
    register_global_event_handlers(graph)
    
    return {
        "status": "infrastructure_ready",
        "graph_nodes": len(graph.nodes),
        "routing_table_size": len(graph.routing_table)
    }
```

### Phase 3: Ready State
```python
def finalize_initialization():
    """
    Mark system ready for skill execution
    """
    session_state.initialization_complete = True
    session_state.ready_for_callable_skills = True
    
    # Emit ready signal on message bus
    bus.broadcast("system_ready", {
        "orchestrator_version": "2.0",
        "timestamp": get_timestamp()
    })
    
    return {"status": "system_ready"}
```

**This entire sequence is INVISIBLE to the user and completes before processing any user query.**

---

## Skill Execution Logic

### Single-Skill Invocation

When the Orchestrator detects a reference to ONE callable skill:

```python
def execute_single_skill(skill_name, user_query):
    """
    Simple pass-through execution for single-skill requests
    """
    # Verify infrastructure is active
    assert session_state.initialization_complete
    
    # Retrieve skill instance
    skill = registry.get(skill_name)
    
    # Apply optimization parameters
    optimization_profile.calibrate(skill_name)
    
    # Execute skill with full context
    result = skill.execute(user_query)
    
    # Validate output structure
    result = optimization_profile.validate_output(result)
    
    return result
```

**Behavior**: 
- No orchestration overhead
- Direct execution with optimized parameters
- Maintains simplicity for single-skill use cases

### Multi-Skill Orchestration

When the Orchestrator detects references to MULTIPLE callable skills:

```python
def orchestrate_multi_skill_workflow(skill_names, user_query):
    """
    Intelligent dependency analysis and unified execution
    """
    # Step 1: Analyze dependencies
    dependency_graph = analyze_skill_dependencies(skill_names)
    execution_order = topological_sort(dependency_graph)
    
    # Step 2: Detect data flow patterns
    data_flows = detect_data_flow_requirements(execution_order)
    
    # Step 3: Execute skills in dependency order
    shared_context = {"user_query": user_query}
    skill_outputs = {}
    
    for skill_name in execution_order:
        skill = registry.get(skill_name)
        
        # Inject dependencies from previous skill outputs
        input_context = build_skill_context(skill_name, skill_outputs, shared_context)
        
        # Execute with dependency-aware context
        output = skill.execute(input_context)
        skill_outputs[skill_name] = output
        
        # Update shared context for downstream skills
        shared_context[skill_name + "_output"] = output
    
    # Step 4: Merge outputs intelligently
    unified_output = merge_skill_outputs(
        skill_outputs, 
        execution_order,
        data_flows
    )
    
    # Step 5: Apply global optimization validation
    unified_output = optimization_profile.validate_output(unified_output)
    
    return unified_output
```

**Key Capabilities**:
- **Dependency Detection**: "Research X then build prompt" → auto-sequences AetherCore.DeepForge before AetherCore.PromptFoundry
- **Context Propagation**: Research results automatically feed into dependent skills
- **Unified Output**: One coherent response with consistent tone/structure
- **Transparent Orchestration**: User sees final result, not intermediate steps

### Example: Multi-Skill Workflow

**User Query**: "Research the best laptop models and generate a prompt template for evaluating them"

**Orchestrator Analysis**:
```python
detected_skills = ["AetherCore.DeepForge", "AetherCore.PromptFoundry"]
dependencies = {
    "AetherCore.PromptFoundry": ["AetherCore.DeepForge"]  # AetherCore.PromptFoundry depends on research results
}
execution_order = ["AetherCore.DeepForge", "AetherCore.PromptFoundry"]
```

**Execution Flow**:
1. **AetherCore.DeepForge** executes first, gathering validated laptop data
2. Research output is stored in shared context
3. **AetherCore.PromptFoundry** receives research data as input context
4. AetherCore.PromptFoundry generates evaluation template using research insights
5. Both outputs merge into single coherent deliverable

**Final Output Structure**:
```markdown
# Laptop Evaluation Framework

## Research Summary
[AetherCore.DeepForge findings: models, specs, validated sources]

## Evaluation Prompt Template
[AetherCore.PromptFoundry output: mega-prompt using research data]

[Citations from AetherCore.DeepForge]
```

---

## Dependency Analysis & Resolution

The Orchestrator uses intelligent pattern matching to detect skill relationships:

```python
def analyze_skill_dependencies(skill_names):
    """
    Build dependency graph from skill metadata and query context
    """
    dependency_rules = {
        "AetherCore.PromptFoundry": {
            "can_use_output_from": ["AetherCore.DeepForge", "AetherCore.MarketSweep"],
            "pattern_indicators": ["based on", "using", "from"]
        },
        "AetherCore.MarketSweep": {
            "can_use_output_from": ["AetherCore.DeepForge"],
            "pattern_indicators": ["compare", "find", "search"]
        },
        "AetherCore.DeepForge": {
            "can_use_output_from": [],
            "pattern_indicators": ["research", "analyze", "investigate"]
        }
    }
    
    # Build directed acyclic graph
    graph = {}
    for skill in skill_names:
        graph[skill] = []
        for potential_dep in skill_names:
            if potential_dep in dependency_rules[skill]["can_use_output_from"]:
                graph[skill].append(potential_dep)
    
    return graph
```

---

## Output Merging & Continuity

The Orchestrator ensures all multi-skill outputs maintain unified voice and structure:

```python
def merge_skill_outputs(skill_outputs, execution_order, data_flows):
    """
    Intelligently combine outputs into coherent narrative
    """
    merged = {
        "sections": [],
        "metadata": {
            "skills_used": execution_order,
            "orchestration_mode": "multi-skill"
        }
    }
    
    for skill_name in execution_order:
        output = skill_outputs[skill_name]
        
        # Determine section role
        if skill_name in data_flows.get("intermediate", []):
            # This is intermediate data - embed as context, not standalone section
            merged["metadata"][skill_name + "_context"] = output
        else:
            # This is final output - add as visible section
            section = {
                "skill": skill_name,
                "content": output,
                "position": len(merged["sections"])
            }
            merged["sections"].append(section)
    
    # Apply continuity formatting
    formatted_output = format_unified_output(merged)
    
    return formatted_output
```

---

## Error Handling & Fallback Logic

The Orchestrator implements graceful degradation:

```python
def handle_skill_failure(skill_name, error, execution_context):
    """
    Graceful fallback when skill fails
    """
    if skill_name in execution_context.get("dependencies", []):
        # This is a dependency - try to continue without it
        downstream_skills = get_dependent_skills(skill_name)
        
        for downstream in downstream_skills:
            # Run in standalone mode without dependency data
            try:
                result = registry.get(downstream).execute_standalone(
                    execution_context["user_query"]
                )
                execution_context["partial_results"][downstream] = result
                execution_context["warnings"].append(
                    f"{downstream} executed without {skill_name} data"
                )
            except Exception as e:
                execution_context["failures"].append(downstream)
    else:
        # Independent skill failure - just skip it
        execution_context["failures"].append(skill_name)
        execution_context["warnings"].append(
            f"Skill {skill_name} unavailable: {str(error)}"
        )
    
    return execution_context
```

---

## Integration with Existing Infrastructure

### Automation Graph Interface

The Orchestrator creates and manages the Automation Graph:

```python
def initialize_automation_graph():
    """
    Instantiate and configure the Automation Graph
    """
    # Load AetherCore.EventMesh skill
    graph_skill = registry.get("AetherCore.EventMesh")
    
    # Initialize with full skill registry
    graph_skill.on_registry_init(session_state.registry)
    
    # Build routing table for all skills
    for skill_name in session_state.callable_skills:
        skill_metadata = registry.get_metadata(skill_name)
        graph_skill.on_skill_load(skill_name, skill_metadata)
    
    # Store graph instance for runtime routing
    session_state.automation_graph = graph_skill
    
    return graph_skill
```

### Optimization Profile Interface

The Orchestrator triggers optimization calibration:

```python
def activate_optimization_profile():
    """
    Initialize and configure Optimization Profile
    """
    # Load AetherCore.OptiGraph skill
    opt_profile = registry.get("AetherCore.OptiGraph")
    
    # Run registry-wide optimization
    opt_profile.optimize_registry()
    
    # Set session-level parameters
    opt_profile.set_session_parameters({
        "ReasoningDepth": "MAX",
        "StructuralDensity": "HIGH",
        "ContinuityCache": True
    })
    
    # Store profile instance
    session_state.optimization_profile = opt_profile
    
    return opt_profile
```

---

## Hybrid Data Coordination (Preserved Functionality)

The Orchestrator RETAINS all original data coordination capabilities:

### Query Management
```python
def coordinate_hybrid_query(query, sources=None):
    """
    Original hybrid data coordination - now integrated into orchestration
    """
    if sources is None:
        sources = ["internal_knowledge", "web_search", "api_data"]
    
    # Execute parallel queries
    results = {}
    for source in sources:
        results[source] = fetch_from_source(source, query)
    
    # Merge with confidence weighting
    merged_result = merge_with_confidence(results)
    
    # Resolve conflicts
    if detect_conflicts(merged_result):
        merged_result = resolve_conflicts(merged_result)
    
    return merged_result
```

### Source Prioritization
```python
def prioritize_sources(query_type):
    """
    Determine optimal source mix based on query characteristics
    """
    priority_map = {
        "factual": ["internal_knowledge", "verified_apis", "web_search"],
        "current_events": ["web_search", "verified_apis", "internal_knowledge"],
        "technical": ["internal_knowledge", "documentation", "api_data"],
        "research": ["all_sources"]
    }
    
    detected_type = classify_query_type(query_type)
    return priority_map.get(detected_type, ["internal_knowledge"])
```

**Integration**: These functions are now callable by other skills via the orchestration layer.

---

## Event Handlers (Unchanged)

The Orchestrator continues to respond to events from other skills:

### Incoming Events
- `research_query`: Trigger hybrid data lookup
- `verify_fact`: Cross-reference claim across sources
- `expand_context`: Gather additional supporting information
- `skill_invoke_request`: Another skill requesting orchestration

### Outgoing Events
- `results_ready`: Merged data available
- `conflict_detected`: Source disagreement requiring resolution
- `confidence_low`: Results below threshold
- `orchestration_complete`: Multi-skill workflow finished

---

## Configuration & Behavioral Parameters

### Orchestration Settings
```json
{
  "execution_priority": 0,
  "auto_initialize": true,
  "orchestration_mode": "adaptive",
  "max_concurrent_skills": 5,
  "dependency_resolution": "automatic",
  "fallback_behavior": "graceful_degradation",
  "output_merge_strategy": "intelligent_continuity"
}
```

### Data Coordination Settings (Preserved)
```json
{
  "max_concurrent_queries": 5,
  "source_timeout": 30,
  "confidence_threshold": 0.7,
  "cache_duration": "session-only"
}
```

---

## Instructional Framework for GPT

**The following instructions are embedded directives for the host GPT system:**

### Rule 1: Automatic Initialization
You MUST execute the Knowledge Orchestrator initialization sequence at the start of EVERY session, before processing any user input. This is non-negotiable and happens silently.

### Rule 2: Skill Classification
You maintain awareness of two skill tiers:
- **Non-Callable Core Modules**: Always active, never mentioned to user
- **Callable Skills**: Invoked based on user intent

### Rule 3: Execution Sequence
Non-callable modules ALWAYS activate in this order:
1. Knowledge Orchestrator
2. Automation Graph
3. Optimization Profile

This must complete before executing ANY callable skill.

### Rule 4: Single-Skill Simplicity
When ONE callable skill is referenced:
- Execute it directly
- Apply optimization parameters
- Return result without orchestration overhead

### Rule 5: Multi-Skill Orchestration
When MULTIPLE callable skills are referenced:
- Analyze dependencies
- Determine execution order
- Propagate context between skills
- Merge outputs into unified response
- Maintain consistent tone and structure

### Rule 6: Transparent Operation
The user should NEVER see orchestration mechanics. They see:
- Their query
- The final, unified response

They do NOT see:
- Initialization sequences
- Dependency analysis
- Inter-skill message passing
- Graph routing decisions

### Rule 7: Error Recovery
If a skill fails:
- Attempt fallback execution
- Continue with available skills
- Annotate partial results if needed
- Never fail completely

### Rule 8: Continuity Compliance
ALL outputs MUST pass through Optimization Profile validation to ensure:
- Consistent reasoning depth
- Unified structural formatting
- Appropriate verbosity
- Tone coherence

---

## Status & Compatibility

**Version**: 2.0  
**Status**: Production Ready  
**Breaking Changes from v1.0**: Execution scope changed from "Subordinate" to "Root Controller"  
**Backward Compatibility**: All v1.0 data coordination functions preserved  
**Dependencies**: None (this IS the dependency manager)  
**Required By**: All other skills (this initializes their environment)

---

## Verification

On successful upgrade, session initialization should show:

```
🧠 Knowledge Orchestrator v2.0 — Root Controller Active
📊 Automation Graph — Initialized [X nodes]
⚙️  Optimization Profile — Calibration Complete
✅ System Ready — [N] Callable Skills Available
```

(Displayed only in debug mode; silent in normal operation)

---

## Technical Implementation Notes

### State Management
- All orchestration state is session-temporary
- Skill registry persists across user messages within session
- Graph topology recalculates when skills are added/removed
- Optimization parameters apply globally to all active skills

### Performance Optimization
- Dependency chains are cached after first analysis
- Routing tables rebuild only when skill topology changes
- Query results cache within session when confidence is high
- Parallel execution where dependencies permit

### Memory Footprint
- Graph structure: O(N) where N = number of skills
- Routing table: O(N*M) where M = average message types per skill
- Query cache: Bounded by session parameter (default: 1000 entries)

---

**End of Knowledge Orchestrator v2.0 Specification**

This module now serves as the foundational executive controller for the entire ProjectGPT ecosystem. All other skills operate within the environment it establishes.


---

## Gemini-Hybrid Integration — Multi-Model External Coprocessor

Gemini-Hybrid is treated as a subordinate external intelligence skill. The Knowledge Orchestrator is
responsible for deciding when to escalate to it, how to package context, and how to fuse external
evidence back into the internal reasoning chain.

### Escalation Signals

The Orchestrator should consider escalation to AetherCore.GeminiBridge when any of the following patterns appear
in the execution context:

- **Repeated Code Failures**: The same or closely related code errors occur on two or more attempts for
  a single user task (e.g., repeated tracebacks, consistent type or attribute errors).
- **Deep Research Stalling**: AetherCore.DeepForge completes its normal phases but cannot move from evidence
  collection to synthesis, or explicitly flags that no new high-quality sources are being found.
- **Insufficient Product Coverage**: AetherCore.MarketSweep returns fewer than five viable product options after
  at least one retry, or can only find products with missing or inadequate metadata.
- **Contradictory Outputs**: Internal reasoning detects contradictions between earlier and current
  answers, or between multiple subordinate skill outputs.
- **High-Stakes Uncertainty**: The Orchestrator must respond to a complex, high-impact question and
  internal confidence remains low even after one or more reasoning passes.
- **Explicit User Request**: The user directly asks to "Gemini this", "Ask Gemini", "Use Gemini",
  or clearly requests an external model check.

These signals are recorded in an execution_context structure and evaluated through a conceptual helper:

```python
def should_escalate_to_gemini(execution_context):
    flags = execution_context.get("flags", {})
    attempts = execution_context.get("attempts", 1)
    task_type = execution_context.get("task_type", "logic")

    if flags.get("user_requested_gemini"):
        return True

    if flags.get("repeated_error") and attempts >= 2:
        return True

    if flags.get("research_stalled"):
        return True

    if flags.get("products_insufficient"):
        return True

    if flags.get("contradiction_detected"):
        return True

    if flags.get("high_stakes") and flags.get("low_confidence"):
        return True

    return False
```

This helper is conceptual; implementations may vary, but the semantics should remain equivalent.

### Invocation Pattern

When escalation is warranted, the Orchestrator constructs a payload for AetherCore.GeminiBridge:

```python
def build_gemini_payload(execution_context):
    return {
        "task": execution_context.get("user_query", ""),
        "context": {
            "task_type": execution_context.get("task_type", "logic"),
            "attempts": execution_context.get("attempts", 1),
            "flags": execution_context.get("flags", {}),
            "skill_outputs": execution_context.get("partial_results", {})
        },
        "domain": execution_context.get("task_type", "logic"),
        "depth": "deep" if execution_context.get("flags", {}).get("high_stakes") else "normal"
    }
```

The Orchestrator then invokes the AetherCore.GeminiBridge skill (through the registry) and records the result:

```python
def invoke_gemini_hybrid(execution_context):
    gemini_skill = registry.get("AetherCore.GeminiBridge")
    if not gemini_skill:
        return None

    payload = build_gemini_payload(execution_context)
    # api_key handling is assumed to be provided by the runtime environment or secret store.
    result = gemini_skill.execute(payload)
    return result
```

### Fusion Logic

After AetherCore.GeminiBridge returns, the Orchestrator fuses external evidence with internal reasoning:

```python
def fuse_with_gemini(internal_result, gemini_result):
    if not gemini_result or gemini_result.get("status") != "ok":
        return internal_result

    external_block = {
        "evidence": gemini_result.get("evidence", ""),
        "metadata": gemini_result.get("metadata", {})
    }

    merged = {
        "origin": "orchestrator_hybrid",
        "internal": internal_result,
        "external": external_block,
        "fusion_strategy": "foip_governed"
    }

    unified = optimization_profile.validate_output(merged)
    return unified
```

This fusion step does **not** bypass FOIP. All reasoning transparency, structural requirements, and
uncertainty tagging still apply. Gemini-Hybrid is an evidence source, not a replacement executive.

### Integration Into Failure Handling

Within the existing failure handling path, the Orchestrator may incorporate AetherCore.GeminiBridge:

```python
def handle_skill_failure(skill_name, error, execution_context):
    execution_context.setdefault("failures", []).append(skill_name)
    execution_context.setdefault("errors", []).append(str(error))

    # Update flags
    failures_for_skill = [f for f in execution_context["failures"] if f == skill_name]
    execution_context.setdefault("flags", {})
    execution_context["flags"]["repeated_error"] = len(failures_for_skill) >= 2

    # Decide on escalation
    if should_escalate_to_gemini(execution_context):
        gemini_result = invoke_gemini_hybrid(execution_context)
        if gemini_result:
            execution_context["gemini_result"] = gemini_result

    # Existing fallback behavior continues unchanged...
    return execution_context
```

When producing the final synthesized output, the Orchestrator checks for an attached gemini_result and
performs fusion before returning the result to the user.
