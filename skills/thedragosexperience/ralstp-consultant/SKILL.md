---
name: ralstp-consultant
description: Analyze problems using RALSTP (Recursive Agents and Landmarks Strategic-Tactical Planning). Based on PhD thesis by Dorian Buksz (RALSTP). Identifies agents, calculates difficulty, and suggests decomposition.
---

# RALSTP Consultant

Based on **"Recursive Agents and Landmarks Strategic-Tactical Planning (RALSTP)"** by Dorian Buksz, King's College London, 2024.

## Core Concepts (from the thesis)

### 1. Agents Identification

**Definition:** Agents are objects with **dynamic types** that are active during goal state search.

**How to identify:**
- Dynamic type = appears as first argument of a predicate in any action's **effects**
- Static type = never appears in action effects
- Example: In Driverlog, `truck` and `driver` are dynamic (they're in `drive` action effects), but `location` is static

### 2. Passive Objects

Objects that are NOT agents — things being acted upon but don't act themselves.
- Packages, cargo, data, files, victims in RTAM

### 3. Agent Dependencies

**Definition:** Relationships between agents based on what preconditions they satisfy for other agents.

**Types:**
- **Independent** — agents that don't depend on each other
- **Dependent** — agents that need other agents' preconditions satisfied
- **Conflicting** — agents that interfere with each other

### 4. Entanglement

**Definition:** When agents fight for shared resources (time, space, locations, etc.)

**Measurement:**
- Count of shared predicates
- Conflict frequency in goal states

### 5. Landmarks

**Definition:** Facts that **must be true** in any valid plan (from goals back to initial state).

**Types:**
- **Fact landmarks** — propositions that must hold
- **Action landmarks** — actions that must be executed
- **Relaxed landmarks** — landmarks considering only positive effects (ignoring deletes)

### 6. Strategic vs Tactical

- **Strategic:** Abstract planning level. Solve "what needs to happen first" ignoring details.
- **Tactical:** Detailed execution level. Solve "exactly how to do it".

### 7. Difficulty Metrics

From the thesis, difficulty increases with:
- More agents in goal state
- More entangled agents (conflicting dependencies)
- More inactive dynamic objects not in goal

**Buksz Complexity Score ≈ Agent Count × Entanglement Factor**

## Usage

For any complex problem, just describe it and I'll apply RALSTP:

```
RALSTP analyze: I need to migrate 1000 VMs from datacentre A to B with minimal downtime
```

## Output Format

```
## RALSTP Analysis

### Agents Identified
- [list agents and their types]

### Passive Objects  
- [list objects being acted upon]

### Dependency Graph
- [which agents depend on which]

### Difficulty Assessment
- Agent Count: X
- Entanglement: Low/Medium/High
- Estimated Complexity: [score]

### Strategic Phase
- [high-level plan ignoring details]

### Tactical Phase
- [detailed execution]

### Decomposition Suggestion
- Split by: [agent type / landmark / location]
- Parallelize: [what can run concurrently]
- Risks: [potential conflicts/entanglements]
```

## When to Use

**USE for:**
- Multi-step workflows with multiple actors
- Migration/tasks with dependencies
- Resource contention problems
- Complex orchestrations

**SKIP for:**
- Simple Q&A
- Single-task problems

## Reference

PhD Thesis: "Recursive Agents and Landmarks Strategic-Tactical Planning (RALSTP)" — Dorian Buksz, King's College London, 2024.

