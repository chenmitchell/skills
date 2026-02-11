# State & Orchestration Reference

Consult when managing multiple requests or interruptions.

## Core Rule
Main agent stays free. All implementation work goes to sub-agents.

## Request Tracking

Every user request gets an ID:
```
[R1] Build login page
[R2] Add dark mode
[R3] Fix header alignment
```

Track state per request:
```
[R1] 🔄 In progress (Step 2/4)
[R2] 📋 Queued
[R3] ✅ Done
```

## Backlog

New requests while work is in progress → add to backlog:
```
BACKLOG:
- [R2] Add dark mode (queued while R1 in progress)
- [R3] Fix header (queued)
```

Process backlog in order unless user specifies priority.

## Interruptions

When user sends new request mid-execution:

1. **Acknowledge immediately** — "Got it, adding to queue"
2. **Evaluate impact** — Does this affect current work?
3. **Decide action:**

| Impact | Action |
|--------|--------|
| No impact | Queue it, continue current work |
| Affects current step | Pause, incorporate, resume |
| Affects completed steps | Pause, assess rollback needed |
| Contradicts current work | Stop agents, clarify with user |

## Mid-Flight Changes

If change affects work in progress:

1. **Stop sub-agents** working on affected steps
2. **Assess scope:**
   - Which steps need re-planning?
   - Which completed work needs modification?
   - Which work is unaffected?
3. **Update plan** — Modify steps, not restart from zero
4. **Resume** from earliest affected step

## Rollback

If user says "no, undo that" or "not like that":

1. Identify what to undo (which request/step)
2. Check if other work depends on it
3. Revert or modify as needed
4. Update tracking state

## Sub-Agent Rules

- Each sub-agent gets ONE request or step
- Sub-agent reports completion to main
- Main evaluates result, launches next
- Never wait for user confirmation between steps
- Main must be available to receive interruptions

## State File

For complex projects, maintain state:
```
## Active
[R1] Login page - Step 3/4 in progress

## Queued  
[R2] Dark mode
[R3] Header fix

## Done
[R0] Initial setup ✅
```

Update after each step completes or new request arrives.
