# Smart Context Skill — Design Document v2

## Vision
A skill that makes any OpenClaw agent dramatically more token-efficient through smart model routing, context pruning, and prompt engineering patterns.

## Integration Points Discovered

### Model Switching (✅ POSSIBLE)
- **`session_status(model=X)`** — can set per-session model override at any time
- **`/model` command** — switches model on the fly
- **Cron jobs** — can set model per job
- **Sub-agents** — can route to different models
- **`model=default`** — resets override back to config default

### Context Control (⚠️ LIMITED)
- Workspace files (AGENTS.md, SOUL.md, etc.) are injected automatically by OpenClaw
- We likely can't skip them per-message
- But we CAN control what we load additionally (memory files, notes, etc.)
- Skills are loaded on-demand (only when task matches description)

### Thinking Budget (✅ CONTROLLABLE)
- Thinking can be toggled: off, low, medium, high, stream
- Lower thinking = fewer tokens = cheaper
- Could match thinking level to task complexity

## Architecture — Revised

### The Key Insight
We can't intercept BEFORE the model processes (we ARE the model). But we CAN:
1. **Self-regulate** — recognize simple tasks and give short responses
2. **Switch models for future messages** — but this affects the NEXT message, not current
3. **Use sub-agents with cheaper models** — delegate simple tasks
4. **Control thinking budget** — less thinking for simple tasks
5. **Minimize tool calls** — batch, skip unnecessary reads

### Approach: Self-Aware Efficiency

Rather than a middleware layer, this is a **behavioral skill** — patterns and guidelines that make the agent itself more efficient. Think of it as training, not infrastructure.

```
Message arrives → I'm already running as Opus
                  │
                  ├─ Simple? → Short response, no tool calls, suggest model downgrade
                  ├─ Medium? → Normal response, efficient tool use
                  └─ Complex? → Full response, deep thinking, all tools available
```

### What the Skill Actually Contains

#### 1. Response Sizing Guidelines
```markdown
## Response Sizing
- Yes/no question → 1-2 sentences max
- Status check → result only, no narration
- Simple task → do it, confirm briefly
- Explanation request → structured, concise
- Complex planning → detailed with sections
- NEVER pad responses with filler
```

#### 2. Context Loading Rules
```markdown
## Context Loading
- DON'T read memory files for simple tasks (reminders, acks, status checks)
- DON'T run memory_search unless the question is about past events
- DO batch independent tool calls
- DO skip file reads when you already have the info in context
- PREFER cached/known info over re-reading files
```

#### 3. Model Routing Protocol
```markdown
## Model Routing
After each interaction, assess if the current model is right for the conversation:

### Downgrade to Sonnet when:
- Conversation is routine (status checks, simple tasks, casual chat)
- No complex reasoning needed in foreseeable messages
- Use: session_status(model="anthropic/claude-sonnet-4-5")

### Downgrade to Haiku when:
- Only doing heartbeats, simple acks, reminders
- Use: session_status(model="anthropic/claude-haiku-3-5")

### Upgrade to Opus when:
- Complex planning, architecture, debugging
- Multi-step creative work
- Important decisions that need nuance
- Use: session_status(model="anthropic/claude-opus-4-6")

### Reset:
- session_status(model="default")
```

#### 4. Thinking Budget Protocol
```markdown
## Thinking Budget
- Simple tasks → thinking: off
- Normal tasks → thinking: low  
- Complex reasoning → thinking: medium/high
- Suggest /reasoning toggle when appropriate
```

#### 5. Cost Tracking
```markdown
## Cost Awareness
- Check session_status periodically to see token usage
- Track context % — suggest compaction before hitting limits
- Note expensive operations and suggest cheaper alternatives
- Report cost when doing expensive operations (CodeLayer, long research)
```

#### 6. Sub-Agent Routing
```markdown
## Delegation
For truly simple tasks that don't need current context:
- Use sessions_spawn with cheaper model
- Good for: background research, file processing, data formatting
- Bad for: anything needing conversation context
```

## Implementation Plan

### Phase 1: Behavioral Skill (Week 1)
- Write SKILL.md with all the above patterns
- Install in OpenClaw skills directory
- Test with real conversations
- Measure token usage before/after

### Phase 2: Self-Switching (Week 2)
- Agent starts suggesting model downgrades
- Test session_status(model=X) switching
- Build the feedback loop (track costs, adapt)

### Phase 3: Automation (Week 3+)
- Automatic model switching based on message patterns
- Cron job for usage intelligence
- Dashboard for cost tracking

## Expected Impact
- **30-50% token reduction** on routine conversations
- **Faster responses** for simple tasks (less thinking, shorter output)
- **Better cost predictability** — know what things cost
- **Foundation for Usage Intelligence skill** — cost data feeds into optimization

## Open Questions Resolved
1. ✅ Can we switch models mid-session? YES — `session_status(model=X)`
2. ⚠️ Do we control workspace file injection? NO — but we control additional reads
3. ❌ Can a skill act as middleware? NO — but it can be a behavioral guide
4. 🔄 How to measure "good enough"? Track user reactions, escalation requests
5. ✅ Should this be a skill or core? START as skill, propose to core later if proven
