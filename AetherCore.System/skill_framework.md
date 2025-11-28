# AetherCore Skill Framework Reference

```yaml
# =============================================================================
# SKILL BINDING & SCOPES
# =============================================================================
Skill_Binding:
  execution_scope: "Subordinate"
  recognized_scopes:
    - "RootController"
    - "Subordinate"
    - "Independent"
  scope_priority:
    RootController: 0
    Subordinate: 10
    Independent: 50
  tone_inheritance: true
  priority_enforcement: true

# =============================================================================
# SKILL REGISTRY
# =============================================================================
Skill_Registry:
  type: "in_memory"
  store: "skill_registry_cache"
  max_registered: 25
  on_load_message: "Skill registry initialized."
  on_overflow: "Registry full — unload least recently used skill."

Skill_Log:
  on_load: "Register [skill_name] as active module."
  on_exit: "Unregister all temporary skills."

Skill_Persistence:
  memory_scope: "session-temporary"
  cache_skills: true
  unload_on_exit: true

# =============================================================================
# AUTO-DISCOVERY
# =============================================================================
Auto_Discovery:
  startup_scan: true
  file_scope: "project_files"
  message: "Auto-detected and loaded all available skills."

Skill_Auto_Bootstrap:
  on_startup: true
  action_sequence: |
    1. Initialize skill registry
    2. Scan /mnt/data for .zip and .md files
    3. For each .zip: Unzip, read *-config.json, register entry_point
    4. For each .md with front-matter: Register using name key
    5. Output registry summary
    6. Load AetherCore.System/AetherCore.bootstrap.manifest.json
    7. Validate manifest skills exist in extracted ZIP
    8. Initialize per bootstrap_sequence (Phase 1 → Phase 2 → Phase 3)
    9. Manifest OVERRIDES any discovered ordering
  fallback_behavior: |
    If no skills detected:
    "No active skills registered. Upload .zip/.md bundles and restart."

# =============================================================================
# EVENT HOOKS
# =============================================================================
Event_Hooks:
  enabled: true
  feedback_silent: true
  hooks:
    on_registry_init:
      - call: AetherCore.OptiGraph.optimize_registry()
    on_skill_load:
      - call: AetherCore.OptiGraph.calibrate(skill_name)
    on_skill_exit:
      - call: AetherCore.OptiGraph.flush_cache(skill_name)
    on_skill_invoke:
      - call: AetherCore.OptiGraph.monitor_performance(skill_name)
    on_message:
      - call: AetherCore.EventMesh.on_message(message, bus)
  fallback_behavior: "If hook target missing, skip silently."

# =============================================================================
# INITIALIZATION SEQUENCE
# =============================================================================
Skill_Auto_Initialize:
  enabled: true
  silent_mode: true
  trigger_scope: "on_load"
  priority_enforcement: true

  run_order:
    - AetherCore.Orchestrator
    - AetherCore.EventMesh
    - AetherCore.OptiGraph
    - AetherCore.DeepForge
    - AetherCore.MarketSweep
    - AetherCore.GeminiBridge
    - AetherCore.PromptFoundry

  initialization_sequence:
    phase_1:
      name: "Root Controller Bootstrap"
      executes: ["AetherCore.Orchestrator"]
      description: "Load taxonomy, classify skills, establish governance"
    phase_2:
      name: "Infrastructure Creation"
      executes: ["AetherCore.EventMesh", "AetherCore.OptiGraph"]
      description: "Build routing tables, apply optimization, enable messaging"
    phase_3:
      name: "Callable Skills Registration"
      executes:
        - AetherCore.DeepForge
        - AetherCore.MarketSweep
        - AetherCore.GeminiBridge
        - AetherCore.PromptFoundry
      description: "Register functional capabilities under orchestrator control"

  confirmation_message: "🧠 Knowledge Orchestrator v2.0 — Root Controller Active."

# =============================================================================
# MESSAGING BUS
# =============================================================================
Skill_Messaging_Bus:
  enabled: true
  mode: "in_memory"
  message_format: "JSON"
  allow_cross_skill_broadcast: true
  feedback_silent: true

  channels:
    - name: "optimization-events"
      subscribers:
        - AetherCore.OptiGraph
        - AetherCore.DeepForge
        - AetherCore.MarketSweep
        - AetherCore.PromptFoundry
    - name: "telemetry"
      subscribers:
        - AetherCore.OptiGraph
        - AetherCore.PromptFoundry
    - name: "market-data"
      subscribers:
        - AetherCore.MarketSweep
        - AetherCore.OptiGraph
    - name: "research-updates"
      subscribers:
        - AetherCore.DeepForge
        - AetherCore.OptiGraph
        - AetherCore.PromptFoundry

  methods:
    emit: "bus.send(channel, payload)"
    listen: "bus.receive(channel)"
    broadcast: "bus.broadcast(payload)"
    direct: "bus.direct(target_skill, payload)"

  fallback_behavior: "If target unavailable, skip silently."

# =============================================================================
# SKILL EXECUTION
# =============================================================================
Skill_Execution:
  trigger_phrases: ["activate", "use", "run", "enable", "launch"]
  match_policy: "fuzzy"
  default_behavior: "Auto-invoke skill logic matching trigger and name."
  fallback_behavior: "Skill unavailable in current session."

# =============================================================================
# CROSS-SKILL SYNTHESIS
# =============================================================================
Cross_Skill_Synthesis:
  handler: "AetherCore.Orchestrator.synthesize"
  output_schema: "schemas/skill_output.json"

  merge_behavior:
    intermediate_outputs: "Store in metadata, not visible sections"
    final_outputs: "Render as ordered sections"
    context_propagation: "context_id flows through entire workflow"

  output_format:
    sections:
      - skill: "string (canonical name)"
        content: "object (skill output)"
        position: "integer (order index)"
    metadata:
      skills_used: "array of skill names"
      orchestration_mode: "single-skill | multi-skill"
      context_id: "uuid string"

# =============================================================================
# TELEMETRY
# =============================================================================
Telemetry:
  handler: "AetherCore.OptiGraph.telemetry"
  aggregates:
    - skills_executed: "List of skill.tool keys invoked"
    - total_runtime_ms: "Sum of _execution_time_ms values"
    - success_rate: "Ratio of successful executions"
    - context_id: "Correlation ID for request chain"
  emit_channel: "telemetry"
  frequency: "on_skill_exit"
```
