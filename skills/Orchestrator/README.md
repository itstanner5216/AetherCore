# AetherCore.Orchestrator v2.0 — Root Executive Controller

**Version:** 2.0  
**Type:** Core System Controller  
**Compatibility:** Project GPT Universal Skill Integration Framework ≥1.0  
**Breaking Changes:** Yes (from v1.0)

---

## Overview

AetherCore.Orchestrator v2.0 represents a **fundamental architectural upgrade** from a subordinate data coordinator to the **root executive controller** of the entire ProjectGPT ecosystem.

### What Changed from v1.0

| Aspect | v1.0 | v2.0 |
|:---|:---|:---|
| **Role** | Data coordinator | Root system controller |
| **Scope** | Subordinate | Root Controller |
| **Priority** | N/A | 0 (executes first) |
| **Responsibilities** | Merge research data | Govern entire skill ecosystem |
| **Initialization** | On-demand | Automatic, every session |
| **Multi-skill** | Not supported | Intelligent orchestration |

---

## Key Capabilities

### 1. Root Controller Authority
- **Always initializes first** in every session
- Defines and enforces skill taxonomy (core vs callable)
- Establishes mandatory activation sequence
- Governs all other skills' execution

### 2. Skill Taxonomy Management

**Non-Callable Core Modules** (Infrastructure):
- AetherCore.Orchestrator
- AetherCore.EventMesh
- AetherCore.OptiGraph

**Callable Skills** (Functional):
- AetherCore.DeepForge
- AetherCore.PromptFoundry
- AetherCore.MarketSweep

### 3. Automatic Activation Sequence

Every session executes this sequence **silently and automatically**:
```
AetherCore.Orchestrator → AetherCore.EventMesh → AetherCore.OptiGraph
```

This infrastructure MUST be ready before any callable skill runs.

### 4. Intelligent Multi-Skill Orchestration

**Single-Skill Mode** (Preserved Simplicity):
```
User: "Use AetherCore.DeepForge to analyze quantum computing"
→ Direct execution, no orchestration overhead
```

**Multi-Skill Mode** (New Capability):
```
User: "Research the best laptops and create a prompt to evaluate them"
→ Automatic dependency analysis
→ Sequential execution: AetherCore.DeepForge → AetherCore.PromptFoundry
→ Context propagation between skills
→ Unified coherent output
```

### 5. Hybrid Data Coordination (Preserved)

All v1.0 data coordination features remain intact:
- Multi-source query management
- Confidence-weighted result merging
- Source conflict resolution
- Session-based caching

---

## Installation & Upgrade

### Fresh Installation

1. Place the `AetherCore.Orchestrator/` directory in your `skills/` folder
2. Ensure all three files are present:
   - `knowledge_orchestrator.md`
   - `config.json`
   - `README.md`
3. Restart ProjectGPT
4. Verify initialization (debug mode):
   ```
   🧠 Knowledge Orchestrator v2.0 — Root Controller Active
   ```

### Upgrading from v1.0

**IMPORTANT**: This is a breaking change to execution scope.

1. **Backup your current v1.0 installation**
2. Replace v1.0 files with v2.0 files in `skills/AetherCore.Orchestrator/`
3. Update any custom configuration in `config.json`
4. Restart ProjectGPT
5. Verify all skills register correctly

**Backward Compatibility**: All v1.0 data coordination functions are preserved. If you only use single-skill invocations, behavior is identical to v1.0.

---

## Usage

### Automatic Operation (Default)

The Knowledge Orchestrator operates **completely silently** in normal use:

1. Session starts
2. Orchestrator initializes automatically
3. Infrastructure activates (Graph + Profile)
4. System ready for user queries
5. **User never sees this process**

### Single-Skill Invocation

**No change from v1.0** — works exactly the same:

```
"Use Deep Research to investigate [topic]"
"Activate Deal Finder for [product]"
"Generate a prompt for [role]"
```

Behavior: Direct execution with optimization parameters applied.

### Multi-Skill Invocation (New)

**Seamless orchestration** when referencing multiple skills:

```
"Research AI trends and create a technical prompt about them"
→ Deep Research executes first
→ Results feed into AetherCore.PromptFoundry
→ Single unified output delivered
```

```
"Find the best deals on laptops and build an evaluation framework"
→ Deal Finder gathers product data
→ AetherCore.PromptFoundry creates evaluation template using that data
→ Coherent merged response
```

**Key Behaviors**:
- Dependency order determined automatically
- Context flows between skills transparently
- Output maintains consistent tone/structure
- No visible orchestration mechanics

### Manual Data Coordination

You can still invoke hybrid data queries directly:

```
"Use knowledge orchestrator to research [topic] from multiple sources"
"Coordinate verification of [claim] across internal and external data"
```

---

## Integration

### Relationship to Other Skills

**Manages**:
- AetherCore.EventMesh (creates and configures)
- AetherCore.OptiGraph (activates and calibrates)

**Orchestrates**:
- AetherCore.DeepForge
- AetherCore.PromptFoundry
- AetherCore.MarketSweep
- (All callable skills)

**Interfaces With**:
- Skill Messaging Bus (broadcasts system events)
- Event Hooks (triggers lifecycle callbacks)
- USIF Registry (manages skill metadata)

### Event Flow

**System Events**:
```
orchestrator_initialized → infrastructure_ready → system_ready
```

**Skill Events** (Preserved from v1.0):
- `research_query`: Hybrid data lookup
- `verify_fact`: Cross-reference validation
- `expand_context`: Supporting information
- `results_ready`: Data available
- `confidence_low`: Needs clarification

**New Events**:
- `orchestration_start`: Multi-skill workflow beginning
- `skill_dependency_resolved`: Execution order determined
- `orchestration_complete`: Unified output ready

---

## Configuration

### Default Settings (config.json)

```json
{
  "execution_scope": "RootController",
  "execution_priority": 0,
  "auto_initialize": true,
  "orchestration_mode": "adaptive",
  "max_concurrent_skills": 5,
  "dependency_resolution": "automatic",
  "output_merge_strategy": "intelligent_continuity"
}
```

### Customization Options

**Orchestration Behavior**:
- `orchestration_mode`: "adaptive" | "manual" | "disabled"
- `max_concurrent_skills`: 1-10 (default: 5)
- `dependency_resolution`: "automatic" | "explicit"
- `fallback_behavior`: "graceful_degradation" | "strict_failure"

**Data Coordination** (Preserved from v1.0):
- `max_concurrent_queries`: 1-10 (default: 5)
- `source_timeout`: seconds (default: 30)
- `confidence_threshold`: 0.0-1.0 (default: 0.7)

---

## Behavior Examples

### Example 1: Single Skill (No Orchestration)

**User Query**: "Research quantum computing advances"

**Orchestrator Action**:
1. Detect single skill reference: `AetherCore.DeepForge`
2. Apply optimization parameters
3. Execute AetherCore.DeepForge directly
4. Return results

**Output**: Standard research report (identical to v1.0 behavior)

---

### Example 2: Two Skills with Dependency

**User Query**: "Research the top programming languages and build a prompt to teach them"

**Orchestrator Action**:
1. Detect skills: `AetherCore.DeepForge`, `AetherCore.PromptFoundry`
2. Analyze dependency: AetherCore.PromptFoundry can use research output
3. Execute AetherCore.DeepForge first
4. Feed research results into AetherCore.PromptFoundry context
5. Merge outputs intelligently

**Output**:
```markdown
# Programming Language Teaching Framework

## Current Landscape Analysis
[AetherCore.DeepForge: Top languages, trends, adoption data, citations]

## Teaching Prompt Template
[AetherCore.PromptFoundry: Mega-prompt built using research insights]

---
Based on research from [sources]...
```

---

### Example 3: Three Skills, Complex Dependencies

**User Query**: "Find the best gaming laptops, research their specs, then create a comparison prompt"

**Orchestrator Action**:
1. Detect skills: `AetherCore.MarketSweep`, `AetherCore.DeepForge`, `AetherCore.PromptFoundry`
2. Build dependency graph:
   - AetherCore.MarketSweep (independent) → products identified
   - AetherCore.DeepForge (uses AetherCore.MarketSweep output) → specs validated
   - AetherCore.PromptFoundry (uses both) → comparison framework
3. Execute in order: AetherCore.MarketSweep → AetherCore.DeepForge → AetherCore.PromptFoundry
4. Propagate context through chain
5. Deliver unified comparison framework

**Output**: Single coherent document combining product listings, specification research, and evaluation methodology

---

## Error Handling

### Graceful Degradation

If a skill fails during orchestration:

**Scenario**: AetherCore.DeepForge times out, AetherCore.PromptFoundry depends on it

**Orchestrator Response**:
1. Log AetherCore.DeepForge failure
2. Execute AetherCore.PromptFoundry in standalone mode (no research context)
3. Annotate output: "Note: Generated without research data due to timeout"
4. Deliver partial results

**User Experience**: Always gets a response, even if degraded

### Failure Scenarios

| Failure Type | Orchestrator Behavior |
|:---|:---|
| Single independent skill fails | Skip skill, continue with others |
| Dependency skill fails | Run dependent skills in standalone mode |
| Core module fails | Abort with error (cannot proceed safely) |
| Orchestrator itself fails | Fallback to basic USIF operation |

---

## Debug & Monitoring

### Initialization Verification (Debug Mode)

Enable debug output to see initialization:

```
🧠 AetherCore.Orchestrator v2.0 — Root Controller Active
   ├─ Core Modules: 3
   ├─ Callable Skills: 3
   └─ Taxonomy Classification: Complete

📊 AetherCore.EventMesh — Initialized
   ├─ Nodes: 6
   ├─ Routing Table: 18 entries
   └─ Dependency Chains: Cached

⚙️  AetherCore.OptiGraph — Calibration Complete
   ├─ Reasoning Depth: MAX
   ├─ Structural Density: HIGH
   └─ Continuity Cache: ENABLED

✅ System Ready — ProjectGPT v2.0 Operational
```

### Runtime Monitoring

Check orchestration activity:
```
"Show orchestrator status"
→ Active skills, dependency graph, last execution
```

---

## Technical Notes

### State Management
- All state is session-temporary
- Graph topology rebuilds when skills added/removed
- Query cache bounded by session parameters
- Optimization settings persist across user messages

### Performance
- Dependency chains cached after first analysis
- Routing tables rebuild only on topology change
- Parallel execution where dependencies allow
- Query result caching (high-confidence only)

### Memory Footprint
- Graph structure: O(N) where N = skill count
- Routing table: O(N*M) where M = avg message types
- Query cache: Configurable (default: 1000 entries)

---

## Migration Guide (v1.0 → v2.0)

### If You Only Use Single Skills
**No action needed**. Behavior is identical to v1.0.

### If You Want Multi-Skill Orchestration
**No action needed**. Just reference multiple skills in queries. Orchestration is automatic.

### If You Have Custom Integrations
1. Review `config.json` for new parameters
2. Update `execution_scope` awareness (now "RootController")
3. Test multi-skill scenarios
4. Verify event handlers still work

### If You Extend the Orchestrator
1. Preserve v1.0 data coordination functions
2. Add orchestration logic in new methods
3. Maintain backward compatibility
4. Document breaking changes clearly

---

## Support & Troubleshooting

### Common Issues

**Issue**: "Skills not executing in correct order"
**Solution**: Check dependency rules in orchestrator code (line 283-304)

**Issue**: "Orchestrator not initializing first"
**Solution**: Verify `execution_priority: 0` in config.json

**Issue**: "Multi-skill outputs are disjoint, not unified"
**Solution**: Check merge logic in `merge_skill_outputs()` function

### Logs & Data

- Initialization logs: ProjectGPT console
- Runtime logs: `data/orchestrator.log` (if enabled)
- State dumps: `data/orchestrator-state.json` (debug mode)

---

## File Structure

```
AetherCore.Orchestrator/
├── knowledge_orchestrator.md  # Main v2.0 controller logic
├── config.json                # Updated configuration (v2.0)
├── README.md                  # This file
└── data/                      # Runtime logs & state (created on first run)
```

---

## Roadmap

### v2.1 (Planned)
- Parallel skill execution (when no dependencies)
- Custom orchestration strategies
- User-defined skill priority rules

### v3.0 (Future)
- Cross-session state persistence
- Advanced conflict resolution
- Dynamic skill loading/unloading

---

## Status

✅ **Production Ready** (v2.0)

**Tested With**:
- AetherCore.DeepForge v1.0
- AetherCore.PromptFoundry v1.0
- AetherCore.MarketSweep v1.0
- AetherCore.EventMesh v1.1
- AetherCore.OptiGraph v1.0

**Known Issues**: None

---

## License & Attribution

**Author:** ProjectGPT Team  
**Last Updated:** November 11, 2025  
**License:** Proprietary (Project GPT Internal Use)

**Breaking Change Notice**: v2.0 changes fundamental execution model. Review upgrade guide before deploying to production environments.

---

**End of README**

For questions, issues, or feature requests, consult ProjectGPT system documentation or check runtime logs.
