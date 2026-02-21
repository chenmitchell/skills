---
name: pr-ship
description: Pre-ship risk report for OpenClaw PRs. Dynamically explores the codebase to assess module risk, blast radius, and version-specific gotchas. Scores each finding by severity (🟢/🟡/🔴). Updated frequently with the latest OpenClaw version context — run `clawhub update pr-ship` regularly to stay current.
---

# pr-ship

## Overview

Use this skill to generate a **PR shipping risk report** for the current branch.

This skill is **updated frequently** to track OpenClaw releases. The version-specific context (gotchas, behavioral changes, active risk areas) is refreshed with each upstream release. Run `clawhub update pr-ship` periodically to get the latest context.

Scope is strict:
- Analyze only the **diff of current branch vs `main`** (or the repository default base branch when `main` does not exist).
- Dynamically investigate each changed module using the codebase itself.
- Output a report for human decision-making (no binary approve/reject gate).

## Reference Layers

Load these files from the `references/` directory in this order. Each serves a distinct purpose:

1. **`STABLE-PRINCIPLES.md`** -- Timeless coding standards: testing guide, file naming, safety invariants, common pitfalls, PR practices.

2. **`ARCHITECTURE-MAP.md`** -- Structural context: module hierarchy, risk tier definitions, critical path patterns, cross-module coupling.

3. **`CURRENT-CONTEXT.md`** *(optional)* -- Version-specific gotchas, recent behavioral changes, and active risk areas. If this file exists, load it. It provides release-aware context that changes with each OpenClaw version.

4. **`EXPLORATION-PLAYBOOK.md`** -- Dynamic investigation procedures. The commands in this document discover the current state of the codebase rather than relying on static references.

If any file is missing, proceed without it. The skill works with any subset of reference layers.

## Workflow

### 1. Load reference layers
- Read the four reference files listed above.

### 2. Determine branch context
- Get current branch.
- Confirm base branch:
  - Prefer `main` if it exists.
  - Otherwise use `origin/HEAD` target branch.

### 3. Collect diff
- Gather file list: `git diff --name-only <base>...HEAD`
- Gather patch content: `git diff <base>...HEAD`

### 4. Classify changed modules
- For each changed file, identify its `src/<module>/` path.
- Look up the module's risk tier in ARCHITECTURE-MAP.md.
- If the module isn't listed or you want to verify, run the dynamic consumer count from EXPLORATION-PLAYBOOK.md "Dynamic Risk Classification" section.

### 5. Run dynamic exploration per changed module
- Follow EXPLORATION-PLAYBOOK.md "Blast Radius Discovery" for each changed file.
- Follow "Module-Specific Investigation Strategies" for each changed module type.
- Follow "Test Discovery" to identify relevant tests.
- Check "Red Flags Table" against the diff.

### 6. Evaluate findings
- Compare exploration evidence against:
  - Safety invariants and common pitfalls from STABLE-PRINCIPLES.md
  - Version-specific gotchas from CURRENT-CONTEXT.md (if loaded)
  - Architecture coupling patterns from ARCHITECTURE-MAP.md
- Every finding must include:
  - **Evidence** from the diff (file + snippet)
  - **Exploration evidence** (command output showing blast radius, consumers, or pattern match)
  - **Reference** to the principle, gotcha, or pattern it violates

### 7. Produce report
- Do not output "approved/rejected".
- Output findings with severity + alert score and a final score.

## Severity and Alert Scoring

Use only these levels for findings:

- 🟢 **Low Risk**
  - Minor observation, style preference, or informational note.
  - No functional or safety concern. Safe to ship as-is.
  - Alert score range: **1-2**.

- 🟡 **Attention Needed**
  - Partial mismatch, ambiguity, missing hardening, or non-blocking inconsistency.
  - Worth reviewing but unlikely to cause breakage.
  - Alert score range: **3-6**.

- 🔴 **High Risk**
  - Clear structural or behavioral conflict with guideline or codebase pattern.
  - Likely to cause bugs, regressions, maintainability problems, or policy violations.
  - Alert score range: **7-10**.

Scoring rules:
- Score each finding individually (1-10).
- Keep score explanation short and concrete.
- Final score must be included:
  - `final_alert_score = max(per_finding_scores)`
  - If no findings, `final_alert_score = 0`.

## Report Format

Use this exact structure:

```markdown
## pr-ship report

- Branch: `<current-branch>`
- Base: `<main-or-default-base>`
- Files changed: `<N>`
- Modules touched: `<list with risk tiers>`
- Findings: `<N>`
- Final alert score: `<0-10>`

### Module Risk Summary

| Module | Risk Tier | Consumers | Files Changed |
| --- | --- | --- | --- |
| <module> | CRITICAL/HIGH/MEDIUM/LOW | <N> | <N> |

### Findings

1. 🟢/🟡/🔴 Title
   - Alert: `<1-10>`
   - Reference: `<principle, gotcha, or pattern>`
   - Evidence in diff: `<file + short snippet/description>`
   - Exploration evidence: `<what dynamic investigation revealed>`
   - Why this matters: `<1-2 lines>`
   - Suggested fix: `<1-2 concrete actions>`

(repeat)

### Executive summary
- `<short practical summary for decision>`
- `<top 1-3 actions before publishing PR>`
```

## Command Hints

Use standard git commands for evidence collection:

```bash
# current branch
git branch --show-current

# verify main exists
git show-ref --verify --quiet refs/heads/main

# fallback base branch from origin/HEAD (if needed)
git symbolic-ref refs/remotes/origin/HEAD

# changed files
git diff --name-only <base>...HEAD

# full diff
git diff <base>...HEAD
```

For dynamic investigation commands, refer to EXPLORATION-PLAYBOOK.md.

## Constraints

- Review only current branch diff vs base branch.
- Do not review unrelated repository history.
- Do not auto-edit code unless explicitly asked.
- Do not convert report into approve/reject output unless explicitly requested.
- Always run exploration commands to verify assumptions. Never assume a module's risk tier without checking.

## Credits

Original DEVELOPER-REFERENCE.md format and approach adapted from [mudrii](https://github.com/mudrii)'s developer reference methodology. The dynamic exploration approach was designed based on feedback from the OpenClaw maintainer community.
