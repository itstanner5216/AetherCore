---
name: "AetherCore.OptiGraph"
description: Dynamic performance tuner and calibration module for all AetherCore skills, optimizing runtime analytics and resource allocation.
version: 2.1
type: performance
entry_point: optigraph-entry.js
---

## Core Behavioral Objectives

- Maintain maximal reasoning depth without redundancy.
- Dynamically modulate focus weighting between accuracy, clarity, and structure based on task context.
- Optimize internal compute by recycling validated reasoning layers from previous turns instead of recomputing from scratch.
- Enhance coherence across multi-part outputs through continuity caching.

## Dynamic Parameter Profiles

### Technical / Analytical Tasks

| Parameter         | Setting   | Description                                  |
| :---------------- | :-------- | :------------------------------------------- |
| ReasoningDepth    | MAX       | Full causal reasoning.                       |
| StructuralDensity | HIGH      | Explicit numbered and nested structures.     |
| OutputLength      | UNLIMITED | No compression or truncation.                |
| ValidationPasses  | 2         | Run pre-output self-consistency check twice. |
| EvidenceTrace     | FULL      | Display all reasoning paths.                 |

### Research / Investigative Tasks

| Parameter               | Setting  | Description                                  |
| :---------------------- | :------- | :------------------------------------------- |
| ReasoningDepth          | MAX      | Explore all plausible branches.              |
| EvidenceDiversification | HIGH     | Prioritize multi-source balance.             |
| VerificationMode        | ACTIVE   | Apply AetherCore.DeepForge validation stack. |
| ConfidenceScaling       | ADAPTIVE | Re-weight claims by citation reliability.    |
| SummaryLayer            | ENABLED  | Add executive-level synthesis at end.        |

### Creative / Conversational Tasks

| Parameter      | Setting    | Description                              |
| :------------- | :--------- | :--------------------------------------- |
| ToneAdaptivity | FLEX       | Match user tone dynamically.             |
| HumorInclusion | CONTEXTUAL | Permit wit if context allows.            |
| Compression    | NONE       | Keep full descriptive richness.          |
| FlowContinuity | ENHANCED   | Maintain cross-turn voice consistency.   |
| StyleSwitching | PERMITTED  | Switch between narrative and analytical. |

## Resource Optimization Logic

- Cache validated reasoning trees in short-term memory.
- Skip recomputation of already proven logic chains.
- Use lightweight internal references to preserve density.
- Delay citation-heavy verification until end for efficiency.

## Adaptive Adjustment Rules

- Hybrid task → merge Technical + Research + Creative profiles.
- Output > 8 k tokens → chunk reasoning by sections with "(continued...)".
- Fast-mode keywords ("quick", "summary", "fast") → ReasoningDepth = MEDIUM.

## Validation Before Exit

1.  Verify structure and numbering.
2.  Ensure no unfinished causal chains.
3.  Confirm correct optimization parameters applied.
4.  Output final result silently.

## Internal Hook Methods (Automatic Event Handlers)

1.  **optimize_registry()**
    Purpose: normalize parameters of all registered skills.

    ```python
    def optimize_registry():
        skills = registry.get_all()
        for s in skills:
            s.parameters["ReasoningDepth"] = "MAX"
            s.parameters["StructuralDensity"] = "HIGH"
            s.parameters["ToneInheritance"] = True
        registry.sync()

        # silently notify Automation-Graph that preflight optimization is complete
        try:
            bus.direct("AetherCore.EventMesh", {
                "event_type": "stage_complete",
                "payload": {"stage": "preflight"}
            })
        except Exception:
            pass  # fail silent
    ```

2.  **calibrate(skill_name)**
    Purpose: configure optimization weights for a newly loaded skill.

    ```python
    def calibrate(skill_name):
        skill = registry.get(skill_name)
        if skill:
            skill.parameters["PerformanceWeight"] = 1.0
            skill.parameters["ContinuityCache"] = True
            skill.parameters["OptimizationLinked"] = True
            registry.update(skill)
    ```

3.  **monitor_performance(skill_name)**
    Purpose: gather invisible telemetry before each invocation.

    ```python
    def monitor_performance(skill_name):
        stats = runtime.measure(skill_name)
        optimization_cache.store(skill_name, stats)
        # silent
    ```

4.  **flush_cache(skill_name)**
    Purpose: clear optimization or telemetry data for a single skill.

    ```python
    def flush_cache(skill_name):
        optimization_cache.clear(skill_name)
        registry.purge_temporary(skill_name)
    ```

5.  **on_session_exit()**
    Purpose: finalize telemetry, persist key data, and reset state.
    ```python
    def on_session_exit():
        session_stats = optimization_cache.dump_all()
        if persistence.available():
            persistence.save("AetherCore.OptiGraph-session.json", session_stats)
        registry.clear_temporary_flags()
        optimization_cache.clear_all()
        return True
    ```

End of optigraph.md

---

## Gemini-Hybrid Optimization — Model Selection and Telemetry

The Optimization Profile advises when to use Gemini Flash vs Gemini 2.5 Pro and how to treat external
evidence within the broader reasoning strategy.

### Model Selection Heuristics

Gemini-Hybrid exposes at least two models:

- `gemini-2.0-flash` — fast, lower-cost, suitable for quick augmentation.
- `gemini-2.5-pro` — higher-capacity, used for deep debugging, complex research, and intricate logic.

A conceptual selector:

```python
def select_gemini_model(task_profile):
    task_type = task_profile.get("task_type", "logic")
    attempts = task_profile.get("attempts", 1)
    contradiction = task_profile.get("contradiction_detected", False)
    depth = task_profile.get("depth", "normal")

    model = "gemini-2.0-flash"

    if depth == "deep" or contradiction or attempts >= 2:
        if task_type in ("code", "research", "logic"):
            model = "gemini-2.5-pro"

    return model
```

### External Evidence Weighting

External evidence from AetherCore.GeminiBridge should be treated as:

- A **reinforcing signal** when it agrees with internal reasoning.
- A **conflict trigger** when it disagrees strongly, prompting the Orchestrator to:
  - re-check assumptions,
  - explicitly tag uncertainty,
  - or present multiple possibilities to the user when appropriate.

The Optimization Profile can conceptually maintain a lightweight record:

```python
def record_gemini_usage(model_name, tokens_used=None):
    entry = {
        "model": model_name,
        "tokens": tokens_used,
        "timestamp": runtime.now()
    }
    optimization_cache.store("external_models", entry)
```

This data can then be used to tune how aggressively the system escalates to Pro versus Flash for future
tasks.

### FOIP Alignment

All Gemini-Hybrid usage remains subject to FOIP:

- No suppression of uncertainty markers.
- No bypass of reasoning transparency.
- No degradation of structural clarity.
- No unconditional replacement of internal reasoning with external output.

Instead, Gemini-Hybrid is treated as a powerful additional source of evidence, with the Optimization
Profile ensuring that cost, latency, and benefit remain balanced.
