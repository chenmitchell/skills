---
name: tiered-memory
description: "Three-tier memory system (hot/warm/cold) for OpenClaw agents. Replaces growing MEMORY.md with fixed-size 5KB hot memory, 50KB scored warm tier, and unlimited Turso cold archive. Use for memory management, consolidation, and intelligent retrieval."
---

# Tiered Memory System

A middleware memory layer for OpenClaw agents. No fork required — works with stock OpenClaw.

## Architecture

```
Hot (MEMORY.md)  ←  5KB, always in context, auto-rebuilt
  ↑ distill
Warm (JSON)      ←  50KB, scored facts, 30-day retention
  ↑ archive
Cold (Turso)     ←  Unlimited, 10-year archive
```

**Tree Index** (~2KB JSON): Hierarchical category map for O(log n) retrieval.

## Setup

The CLI tool is at: `skills/tiered-memory/scripts/memory_cli.py`

### Initialize tree with default categories

```bash
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "owner" "Owner profile and preferences"
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "projects" "Active projects"
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "technical" "Technical setup and config"
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "conversations" "Conversation summaries"
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "lessons" "Lessons learned"
```

### Initialize cold storage (Turso)

```bash
# Get Turso credentials
TURSO_URL=$(memory/decrypt.sh turso-credentials.json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('url',''))" 2>/dev/null)
TURSO_TOKEN=$(memory/decrypt.sh turso-credentials.json 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin).get('token',''))" 2>/dev/null)

python3 skills/tiered-memory/scripts/memory_cli.py cold --init --db-url "$TURSO_URL" --auth-token "$TURSO_TOKEN"
```

## When to Use This Skill

Load this skill when:
- Processing a conversation that should be remembered
- Retrieving past context for a query
- Running periodic maintenance (consolidation)
- Managing memory categories (tree)
- Rebuilding MEMORY.md (hot tier)

## Commands

### Store a fact (after distilling a conversation)

```bash
python3 skills/tiered-memory/scripts/memory_cli.py store \
  --text "Bowen wants to focus on EvoClaw BSC integration for hackathon" \
  --category "projects/evoclaw" \
  --importance 0.8
```

**When to store:** After significant conversations — decisions made, preferences expressed, technical facts learned, action items identified. Don't store routine greetings or simple Q&A.

**Importance guide:**
- 0.9-1.0: Critical decisions, credentials, identity info
- 0.7-0.8: Project decisions, technical architecture, preferences
- 0.5-0.6: General conversation facts, daily events
- 0.3-0.4: Casual mentions, low-priority info

### Retrieve memories

```bash
python3 skills/tiered-memory/scripts/memory_cli.py retrieve \
  --query "EvoClaw hackathon deadline" \
  --limit 5
```

**Multi-tier flow:** Tree index → warm → cold (if Turso configured).

To include cold storage:
```bash
python3 skills/tiered-memory/scripts/memory_cli.py retrieve \
  --query "BSC deployment" \
  --limit 5 \
  --db-url "$TURSO_URL" \
  --auth-token "$TURSO_TOKEN"
```

### Check stats

```bash
python3 skills/tiered-memory/scripts/memory_cli.py stats
```

Returns hot/warm/tree sizes and usage percentages.

### Tree management

```bash
# Show tree structure
python3 skills/tiered-memory/scripts/memory_cli.py tree --show

# Add a category
python3 skills/tiered-memory/scripts/memory_cli.py tree --add "projects/clawchain" "ClawChain L1 blockchain"

# Search tree for relevant categories
python3 skills/tiered-memory/scripts/memory_cli.py tree --search "blockchain BSC"

# Remove empty category
python3 skills/tiered-memory/scripts/memory_cli.py tree --remove "old/category"
```

### Warm memory operations

```bash
# List all warm facts
python3 skills/tiered-memory/scripts/memory_cli.py warm --list

# Search warm facts
python3 skills/tiered-memory/scripts/memory_cli.py warm --search "hackathon"

# Get recent facts
python3 skills/tiered-memory/scripts/memory_cli.py warm --recent 10

# Evict expired facts
python3 skills/tiered-memory/scripts/memory_cli.py warm --evict
```

### Hot state (identity/lessons)

```bash
# Update owner profile
python3 skills/tiered-memory/scripts/memory_cli.py hot-state \
  --key owner \
  --data '{"name": "Bowen", "timezone": "Australia/Sydney", "style": "direct, technical"}'

# Add a lesson
python3 skills/tiered-memory/scripts/memory_cli.py hot-state \
  --key lesson \
  --data '{"text": "Always encrypt credentials before committing"}'

# Add/update project
python3 skills/tiered-memory/scripts/memory_cli.py hot-state \
  --key project \
  --data '{"name": "EvoClaw", "status": "Active - BSC integration", "description": "Self-evolving agent framework"}'
```

### Rebuild MEMORY.md

```bash
python3 skills/tiered-memory/scripts/memory_cli.py rebuild-hot
```

Generates a fresh 5KB MEMORY.md from:
- Hot state (owner, agent, lessons, projects)
- Top warm facts by score
- Enforces 5KB limit by trimming least important content

### Consolidation (periodic)

```bash
python3 skills/tiered-memory/scripts/memory_cli.py consolidate
```

Does:
1. Evicts warm facts past retention (30 days) with low scores
2. Updates tree node counts
3. Rebuilds MEMORY.md

## Agent Workflow

### After important conversations:

1. Distill the key facts from the conversation
2. Store each fact with appropriate category and importance
3. If a new topic emerged, add a tree category

### During heartbeat (every 4-8 hours):

1. Run consolidation
2. Check warm stats — is it getting full?
3. Archive high-value expired facts to cold before they're evicted

### On session start:

1. Run `rebuild-hot` to refresh MEMORY.md
2. Check `stats` to monitor system health

### Monthly:

1. Review tree structure — merge similar categories, add new ones
2. Archive important warm facts to cold storage
3. Clean up dead tree nodes

## Scoring Formula

```
score = importance × recency_decay × reinforcement
recency_decay = exp(-age_days / 30)        # Half-life: 30 days
reinforcement = 1 + 0.1 × ln(1 + access)  # Diminishing returns
```

Facts below 0.3 score after retention period are evicted.

## File Locations

- Tree index: `memory/memory-tree.json` (~2KB)
- Warm facts: `memory/warm-memory.json` (≤50KB)
- Hot state: `memory/hot-memory-state.json` (identity/lessons)
- Output: `MEMORY.md` (≤5KB, auto-generated)
- Cold: Turso database (unlimited)

## Compatibility

- **Zero OpenClaw modifications** — uses standard workspace files and exec
- **Survives updates** — skill + data files, nothing patched
- **Graceful degradation** — works without Turso (warm-only mode)
- **Reversible** — delete skill, keep your original MEMORY.md
