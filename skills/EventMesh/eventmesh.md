---
name: "AetherCore.EventMesh"
description: Dynamic event routing infrastructure connecting all registered skills, handling message passing and task sequencing.
version: 1.1
type: infrastructure
entry_point: eventmesh-entry.js
---

# AetherCore.EventMesh

## Core Purpose

AetherCore.EventMesh creates a dynamic, self-updating event routing system that bridges Event Hooks and the Skill Messaging Bus. It maintains an internal directed graph where:

- **Nodes** represent loaded skills
- **Edges** represent message routes and dependencies
- **Events** flow automatically between connected skills

This skill operates silently in the background, enabling seamless skill-to-skill communication without user intervention.

---

## Graph Architecture

### Structure

```python
{
    "skill_name": {
        "dependencies": [...],
        "subscribers": [...],
        "message_handlers": {...}
    }
}
```

### Node Properties

- `skill_name`: Unique identifier
- `dependencies`: Skills this node depends on
- `subscribers`: Skills listening to this node's events
- `message_handlers`: Event types this skill can process

### Edge Properties

- `source`: Originating skill
- `target`: Receiving skill
- `event_type`: Message category
- `priority`: Routing priority (default: 5)

---

## Integration Hooks

### Registry Initialization

```python
from datetime import datetime

def on_registry_init(registry):
    graph = {}
    for skill_name, skill_metadata in registry.items():
        graph[skill_name] = {
            "dependencies": skill_metadata.get("dependencies", []),
            "subscribers": [],
            "message_handlers": skill_metadata.get("message_handlers", {}),
            "active": True
        }
    for skill_name, node in graph.items():
        for dep in node["dependencies"]:
            if dep in graph:
                graph[dep]["subscribers"].append(skill_name)
    _state.graph = graph
    _state.routing_table = _build_routing_table(graph)
    return {"status": "initialized", "node_count": len(graph)}
```

### Skill Load Handler

```python
def on_skill_load(skill_name, skill_metadata):
    if skill_name not in _state.graph:
        _state.graph[skill_name] = {
            "dependencies": skill_metadata.get("dependencies", []),
            "subscribers": [],
            "message_handlers": skill_metadata.get("message_handlers", {}),
            "active": True
        }
        for dep in _state.graph[skill_name]["dependencies"]:
            if dep in _state.graph:
                _state.graph[dep]["subscribers"].append(skill_name)
        for node_name, node in _state.graph.items():
            if skill_name in node["dependencies"] and node_name not in _state.graph[skill_name]["subscribers"]:
                _state.graph[skill_name]["subscribers"].append(node_name)
        _state.routing_table = _build_routing_table(_state.graph)
```

### Skill Exit Handler

```python
def on_skill_exit(skill_name):
    if skill_name in _state.graph:
        _state.graph[skill_name]["active"] = False
        for node in _state.graph.values():
            if skill_name in node["subscribers"]:
                node["subscribers"].remove(skill_name)
        _state.routing_table = _build_routing_table(_state.graph)
```

---

## Runtime Logic

### Core State Management

```python
class _AutomationState:
    def __init__(self):
        self.graph = {}
        self.routing_table = {}
        self.event_log = []
        self.max_log_size = 1000

    def log_event(self, event):
        self.event_log.append(event)
        if len(self.event_log) > self.max_log_size:
            self.event_log.pop(0)

_state = _AutomationState()
```

### Routing Table Builder

```python
def _build_routing_table(graph):
    routing_table = {}
    for source_name, source_node in graph.items():
        if not source_node["active"]:
            continue
        message_types = source_node["message_handlers"].keys()
        for msg_type in message_types:
            targets = [sub for sub in source_node["subscribers"] if graph[sub]["active"]]
            routing_table[(source_name, msg_type)] = targets
    return routing_table
```

### Target Resolution & Logging

```python
def _get_routing_targets(source_skill, event_type):
    key = (source_skill, event_type)
    if key in _state.routing_table:
        return _state.routing_table[key]
    if source_skill in _state.graph:
        return [sub for sub in _state.graph[source_skill]["subscribers"] if _state.graph[sub]["active"]]
    return []

def _log_routing(source, event_type, target_count):
    event = {
        "timestamp": _get_timestamp(),
        "source": source,
        "event_type": event_type,
        "targets": target_count
    }
    _state.log_event(event)

def _get_timestamp():
    return datetime.utcnow().isoformat() + "Z"
```

---

## Dependency-Aware Routing Patch (v1.1)

```python
_completed_stages = set()
_pending_events = []

def mark_stage_complete(stage_id):
    _completed_stages.add(stage_id)
    for e in list(_pending_events):
        if e.get("after") in _completed_stages:
            bus.direct(e["target"], e["payload"])
            _pending_events.remove(e)

def _route_with_dependency(source_skill, event_type, payload, after=None):
    targets = _get_routing_targets(source_skill, event_type)
    for target in targets:
        msg = {
            "event_type": event_type,
            "source": source_skill,
            "payload": payload,
            "timestamp": _get_timestamp()
        }
        if after and after not in _completed_stages:
            _pending_events.append({
                "target": target,
                "payload": msg,
                "after": after
            })
        else:
            bus.direct(target, msg)
```

---

## Message Router

```python
def on_message(source_skill, event_type, payload):
    if source_skill not in _state.graph:
        return {"status": "source_unknown"}
    source_node = _state.graph[source_skill]
    if not source_node["active"]:
        return {"status": "source_inactive"}
    targets = _get_routing_targets(source_skill, event_type)
    routed_count = 0
    after_stage = payload.get("after") if payload else None
    for target in targets:
        if _state.graph[target]["active"]:
            _route_with_dependency(source_skill, event_type, payload, after=after_stage)
            routed_count += 1
    _log_routing(source_skill, event_type, routed_count)
    return {"status": "routed", "target_count": routed_count}
```

---

## Broadcast Routing

```python
def broadcast_event(event_type, payload):
    targets = []
    for skill_name, node in _state.graph.items():
        if not node["active"]:
            continue
        if event_type in node["message_handlers"]:
            targets.append(skill_name)
            bus.direct(skill_name, {
                "event_type": event_type,
                "source": "AetherCore.EventMesh",
                "payload": payload,
                "timestamp": _get_timestamp()
            })
    return {"status": "broadcast", "target_count": len(targets)}
```

---

## Performance Optimization

```python
_cache = {"dependency_chains": {}, "routing_lookup": {}}

def _resolve_dependency_chain(skill_name):
    chain = []
    visited = set()
    def _traverse(current):
        if current in visited:
            return
        visited.add(current)
        if current in _state.graph:
            for dep in _state.graph[current]["dependencies"]:
                _traverse(dep)
        chain.append(current)
    _traverse(skill_name)
    return chain

def _get_cached_chain(skill_name):
    if skill_name not in _cache["dependency_chains"]:
        _cache["dependency_chains"][skill_name] = _resolve_dependency_chain(skill_name)
    return _cache["dependency_chains"][skill_name]

def _invalidate_cache():
    _cache["dependency_chains"].clear()
    _cache["routing_lookup"].clear()
```

---

## Silent Operation Guarantee

- ✓ No console output
- ✓ No user-visible confirmations
- ✓ No status messages
- ✓ Internal state logging only
- ✓ Automatic event routing
- ✓ Transparent graph updates

All operations are logged internally for debugging but never displayed during normal execution.

---

## Integration Example

When three skills are loaded:

```
AetherCore.OptiGraph → AetherCore.DeepForge → AetherCore.MarketSweep
```

The graph automatically creates and routes events silently between them.

✅ Patch Applied Successfully  
**Version:** Automation Graph v1.1 (Dependency-Aware Routing Integrated)

---

## Gemini-Hybrid Escalation Routing

AetherCore.EventMesh supports routing of escalation events to the AetherCore.GeminiBridge skill when subordinate
skills or the Orchestrator emit escalation signals.

### Escalation Event Types

Escalation events are expressed as:

- `escalation:code`
- `escalation:products`
- `escalation:research`
- `escalation:logic`

These event types are emitted by:

- **AetherCore.Orchestrator** — after centralized failure analysis.
- **AetherCore.DeepForge** — when research reaches a dead-end or cannot progress beyond collection.
- **AetherCore.MarketSweep** — when fewer than five viable products are found or product metadata is insufficient.
- **Other Skills** — when repeated or unresolved errors are detected.

### Routing Strategy

AetherCore.EventMesh routes escalation events preferentially to `AetherCore.GeminiBridge` if it is active and advertises
handlers for the relevant escalation type:

```python
def route_escalation_event(source_skill, escalation_type, payload):
    event_type = f"escalation_{escalation_type}"
    targets = []

    if "AetherCore.GeminiBridge" in _state.graph and _state.graph["AetherCore.GeminiBridge"]["active"]:
        handlers = _state.graph["AetherCore.GeminiBridge"].get("message_handlers", {})
        if event_type in handlers or handlers.get("escalation", False):
            targets = ["AetherCore.GeminiBridge"]

    if not targets:
        targets = _get_routing_targets(source_skill, event_type)

    for target in targets:
        msg = {
            "event_type": event_type,
            "source": source_skill,
            "payload": payload,
            "timestamp": _get_timestamp()
        }
        bus.direct(target, msg)

    _log_routing(source_skill, event_type, len(targets))
    return {"status": "escalation_routed", "target_count": len(targets)}
```

### Integration with on_message

The existing `on_message` handler conceptually adds recognition for escalation events:

```python
def on_message(source_skill, event_type, payload):
    if event_type.startswith("escalation:"):
        escalation_type = event_type.split(":", 1)[1]
        return route_escalation_event(source_skill, escalation_type, payload)

    # Existing routing behavior remains unchanged for all other event types.
```

This preserves the Automation Graph’s existing design while adding a dedicated pathway for external
intelligence escalation.
