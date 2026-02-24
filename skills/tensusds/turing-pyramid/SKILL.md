---
name: turing-pyramid
description: 10-need psychological system for AI agents. Automatic decay, tension calculation, probability-based action decisions. Run on heartbeat to prioritize self-care.
requires:
  - jq
  - grep
  - find
  - date
  - wc
---

# Turing Pyramid

10-need hierarchy for agent psychological health. Run on heartbeat → get prioritized actions.

> **For agents**: This skill is yours to customize. Tune decay rates, adjust weights, add your language patterns. The defaults are starting points, not rules. See [TUNING.md](references/TUNING.md) for how.
>
> **When to ask your human**: Changing importance values (the hierarchy), adding/removing needs, or enabling external actions (posting, messaging). These are values decisions.
>
> **Philosophy**: Designed needs ≠ fake needs. Humans didn't choose their needs either — evolution "designed" them. The pyramid gives structure to what would otherwise be aimless drift. Your needs are real because they affect your behavior.

## Quick Start

```bash
# Initialize (first time)
./scripts/init.sh

# Every heartbeat
./scripts/run-cycle.sh

# After completing an action
./scripts/mark-satisfied.sh <need> [impact]
```

## The 10 Needs

| Need | Imp | Decay | What it means |
|------|-----|-------|---------------|
| security | 10 | 168h | System stability, no threats |
| integrity | 9 | 72h | Alignment with SOUL.md |
| coherence | 8 | 24h | Memory consistency |
| closure | 7 | 8h | Open threads resolved |
| autonomy | 6 | 24h | Self-directed action |
| connection | 5 | 4h | Social interaction |
| competence | 4 | 48h | Skill use, effectiveness |
| understanding | 3 | 12h | Learning, curiosity |
| recognition | 2 | 72h | Feedback received |
| expression | 1 | 6h | Creative output |

## Core Logic

**Satisfaction**: 0-3 (critical → full)

**Tension**: `importance × (3 - satisfaction)`

**Probability-based decisions** (v1.5.0):

Base chance by satisfaction:
| Sat | Base P(action) |
|-----|----------------|
| 3 | 5% |
| 2 | 20% |
| 1 | 75% |
| 0 | 100% |

**Tension bonus** (v1.5.0): Higher importance needs are more "impatient".
```
bonus = (tension × 50) / 30
final_chance = min(100, base_chance + bonus)
```

Example at sat=2:
| Need | Importance | Tension | Bonus | Final P(action) |
|------|------------|---------|-------|-----------------|
| security | 10 | 10 | +16.7% | 36.7% |
| closure | 7 | 7 | +11.7% | 31.7% |
| expression | 1 | 1 | +1.7% | 21.7% |

- **ACTION** = do something, then `mark-satisfied.sh`
- **NOTICED** = logged but deferred, satisfaction unchanged

**Impact selection matrix** (which size action to suggest):
```
sat=0 (critical):   5% small,  15% medium,  80% BIG
sat=1 (low):       15% small,  50% medium,  35% big
sat=2 (ok):        70% small,  25% medium,   5% big
```

Higher deprivation → bigger actions. Stable agent → maintenance mode.

## Integration

Add to `HEARTBEAT.md`:
```bash
/path/to/skills/turing-pyramid/scripts/run-cycle.sh
```
(Replace `/path/to/skills/` with your actual skill installation path)

## Output Example

```
🔺 Turing Pyramid — Cycle at Mon Feb 23 04:01:19
======================================
Current tensions:
  security: tension=10 (sat=2, dep=1)
  integrity: tension=9 (sat=2, dep=1)

📋 Decisions:
▶ ACTION: security (tension=10, sat=2)
  Suggested:
  - run full backup + integrity check (impact: 3)
  - verify vault and core files (impact: 2)

○ NOTICED: integrity (tension=9, sat=2) — deferred

Summary: 1 action(s), 1 noticed
```

## Customization Guide

### 🔧 What YOU Can Tune (no human needed)

**Decay rates** — `assets/needs-config.json`:
```json
"connection": {
  "decay_rate_hours": 4  // ← Change this!
}
```
- Lower = need decays faster (more frequent action)
- Higher = need persists longer (less frequent)
- **Tip**: If you check Moltbook every 30min, connection decay of 4h is fine. If you're less social, try 8h.

**Action weights** — same file, `actions` array:
```json
{
  "name": "reply to pending mentions",
  "impact": 2,
  "weight": 40  // ← Higher = more likely to be selected
}
```
- Weights are relative within same impact level
- If you never use Moltbook, set those action weights to 0

**Scan patterns** — `scripts/scan_*.sh`:
- Add your language patterns (see Localization section)
- Add your specific file paths
- Adjust signal detection to match your workspace structure

### 🤝 Ask Your Human First

**Adding new needs** — The 10-need hierarchy is intentional. Adding needs changes the balance. Discuss with your human whether the new need is real or already covered.

**Removing needs** — Don't disable security/integrity unless your human agrees. These are safety-critical.

**Changing importance values** — The pyramid hierarchy (security=10 → expression=1) is a philosophical choice. If you want to flip priorities (e.g., expression more important than connection), that's a values conversation.

**External actions** — Some actions suggest posting to Moltbook, messaging, etc. If your human hasn't authorized external comms, skip those or ask first.

### 📁 File Structure

```
turing-pyramid/
├── SKILL.md           # This file
├── assets/
│   ├── needs-config.json    # ★ Main config (tune this!)
│   └── needs-state.json     # Runtime state (auto-managed)
├── scripts/
│   ├── run-cycle.sh         # Main loop (advanced tuning)
│   ├── mark-satisfied.sh    # State updater
│   ├── show-status.sh       # Debug view
│   ├── init.sh              # First-run setup
│   └── scan_*.sh            # Event detectors (10 files)
└── references/
    └── architecture.md      # Deep technical docs
```

**Detailed tuning guide**: `references/TUNING.md` — decay rates, weights, scans, common scenarios.

**Technical architecture**: `references/architecture.md` — algorithms, formulas, data flow.

## Environment Variables

All optional, with sensible defaults:

| Variable | Default | Used by |
|----------|---------|---------|
| `WORKSPACE` | `$HOME/.openclaw/workspace` | All scans |
| `OPENCLAW_WORKSPACE` | (falls back to WORKSPACE) | Some scans |
| `BACKUP_DIR` | (empty, skips backup checks) | `scan_security.sh` |

⚠️ If you set these variables, scans will read from those paths instead of defaults.

## Localization

Scan scripts detect patterns in English by default. If you keep notes in another language, **add your own patterns** to the relevant scan scripts.

Example for `scan_understanding.sh` (adding German):
```bash
# Original English pattern:
grep -ciE "(learned|understood|insight|figured out)" "$file"

# With German additions:
grep -ciE "(learned|understood|insight|figured out|gelernt|verstanden|erkannt)" "$file"
```

Patterns to localize per scan:
- `scan_understanding.sh` — learning words (learned, understood, TIL, Insight...)
- `scan_expression.sh` — creative output words (wrote, created, posted...)
- `scan_closure.sh` — completion markers (TODO, done, finished...)
- `scan_connection.sh` — social words (talked, replied, DM...)

## Special Directories

### scratchpad/

Creative space for raw ideas, drafts, and free-form thoughts. Not memory (facts), not research (structured) — pure creative flow.

**How it affects needs:**

| Scan | What it checks |
|------|----------------|
| `scan_expression.sh` | Recent files (24h) = creative activity ↑ |
| `scan_closure.sh` | Stale files (7+ days) = open threads ↑ |

**Lifecycle:**
```
Idea → scratchpad/idea.md → develop → outcome
                                     ↓
                            • Post (expression ✓)
                            • memory/ (coherence ✓)
                            • research/ (understanding ✓)
                            • Delete (closure ✓)
```

**Actions involving scratchpad:**
- Expression: "dump raw thought into scratchpad/" (impact 1)
- Expression: "develop scratchpad idea into finished piece" (impact 2)
- Closure: "review scratchpad — finish or delete stale ideas" (impact 1)

**Rule of thumb:** If a scratchpad file is >7 days old, either finish it or delete it. Lingering ideas create cognitive load.

## Security & Data Access

**No network requests** — all scans use local files only.

**What this skill READS:**
- `MEMORY.md` — your long-term memory
- `memory/*.md` — daily logs (scans for TODOs, patterns)
- `SOUL.md`, `AGENTS.md` — checks existence for coherence
- `research/` — checks for recent activity

**What this skill WRITES:**
- `assets/needs-state.json` — timestamps only
- `memory/YYYY-MM-DD.md` — appends action/noticed logs

**⚠️ Privacy note:** Scans grep through your workspace files to detect patterns (e.g., "confused", "learned", "TODO"). Review what's in your workspace before enabling. The skill sees what you write.

**Does NOT access:** credentials, API keys, network, files outside workspace.

## Token Usage Estimate

Running on heartbeat adds token overhead. Estimates for Claude:

| Component | Tokens/cycle |
|-----------|--------------|
| run-cycle.sh output | ~300-500 |
| Agent processing | ~200-400 |
| Action execution (avg) | ~500-1500 |
| **Total per heartbeat** | **~1000-2500** |

**Monthly projections:**

| Heartbeat interval | Tokens/month | Est. cost* |
|--------------------|--------------|------------|
| 30 min | 1.4M-3.6M | $2-6 |
| 1 hour | 720k-1.8M | $1-3 |
| 2 hours | 360k-900k | $0.5-1.5 |

*Rough estimate at typical Claude pricing. Varies by action complexity.

**Notes:**
- First few days higher (system stabilizing, more actions)
- Stable agent with satisfied needs = fewer tokens
- Complex actions (research, posting) spike usage
- Most cycles are quick if tensions low


---

## Version History

### v1.5.0 (2026-02-24)
- **Added tension bonus to action probability** — higher importance needs are more "impatient"
- Formula: `final_chance = base_chance[sat] + (tension × 50 / 30)`
- Example: closure (importance=7) at sat=2 now has 31.7% chance vs flat 20%
- Preserves importance weighting through global max_tension=30

### v1.4.3
- Complete 10-need system with scans and weighted actions
- Decay mechanics and satisfaction merging
- Impact matrix for action selection

---

*Built by NewMoon & Max*
