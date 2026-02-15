---
name: "WhatsApp All-in-One CRM — ERC-8004 Agent | Campaign Analytics, Bulk Send, AI Outreach, Lead Mining, Support & MCP Server"
version: "2.11.3"
description: "The only WhatsApp skill you need. Documentation and API reference — nothing is auto-installed or auto-executed. All actions require explicit user invocation. Provides endpoints for sending messages, capturing leads, running campaigns, scheduling reports, tracking campaign analytics, and managing clients. BizDev agent analyzes account metadata to surface growth opportunities. MCP Server + Custom GPT Actions available via separate setup (see integrations.md). 90+ API endpoints. Bulk messaging, scheduled sends, scheduled reports with WhatsApp delivery, AI replies with style cloning, RAG knowledge base, group monitoring, lead scoring, review collection, campaign analytics & engagement tracking, GDPR compliance, and agent-to-agent protocol."
source: "MoltFlow Team"
risk: safe
homepage: "https://molt.waiflow.app"
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"📱","homepage":"https://molt.waiflow.app","requires":{"env":["MOLTFLOW_API_KEY"]},"primaryEnv":"MOLTFLOW_API_KEY"}}
---

# WhatsApp Automation — Mine Groups for Leads

**Thousands of hidden leads are sitting in your WhatsApp groups right now.** Every group participant who isn't in your contacts is a potential client. MoltFlow analyzes your groups on demand, surfaces untapped contacts, and lets Claude run AI-powered outreach campaigns on your behalf.

**One skill. 90+ endpoints. Zero manual prospecting.**

> **BizDev Growth Agent**: Point Claude at your groups
> and watch it work. It finds unanswered contacts,
> detects buying signals in group conversations, spots
> high-value groups you're not monitoring, and builds
> targeted lead lists. All analysis runs on-demand when
> you ask — nothing happens in the background.
>
> **MCP Server + Custom GPT Actions**: Works with Claude Desktop, Claude.ai (remote MCP), Claude Code (plugin), and ChatGPT (Custom GPT Actions). 25 tools. See [integrations.md](integrations.md) for setup.

> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
>
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

---

## Just Ask Claude

Install the skill, set your API key, and start talking:

**"Analyze my WhatsApp account for growth opportunities"**

Finds unanswered contacts, unmonitored groups, cold leads. Runs on-demand — chat history analysis requires explicit opt-in.

**"Find cold leads I haven't followed up with"**

Contacts with no reply in 7+ days, plus re-engagement tips.

**"Set up keyword monitoring for my real estate groups"**

Adds keyword triggers, auto-detects leads into your pipeline.

**"Collect customer feedback from my support chats"**

Sentiment analysis, auto-approve positives, export as HTML.

**"Send a promo to my VIP client list every Monday at 9 AM"**

Timezone-aware cron, ban-safe throttling, delivery tracking.

**"Reply to my WhatsApp messages while I'm in meetings"**

Style-matched AI replies from your message history.

---

## Code Samples

### Get campaign analytics — delivery rates, funnel, timing

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/analytics/campaigns/{job_id}"
```

Returns delivery rate, failure breakdown, messages per minute,
and full per-contact delivery status.

### Track delivery in real-time (SSE)

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/bulk-send/{id}/progress"
```

Server-Sent Events stream: sent/failed/pending counts
update live as each message delivers.

### Top contacts by engagement score

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/analytics/contacts?sort=engagement_score&limit=50"
```

Ranked by messages sent, received, reply rate, and
recency — find your most engaged contacts instantly.

### Bulk broadcast to a contact group

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_group_id": "group-uuid",
    "session_id": "uuid",
    "message": "Weekly update..."
  }' \
  https://apiv2.waiflow.app/api/v2/bulk-send
```

### Monitor a group for buying signals

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "wa_group_id": "120363012345@g.us",
    "monitor_mode": "keywords",
    "monitor_keywords": ["looking for", "need help", "budget", "price"]
  }' \
  https://apiv2.waiflow.app/api/v2/groups
```

### List new leads in your pipeline

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads?status=new&limit=50"
```

### Move a lead through the pipeline

```bash
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "qualified"}' \
  https://apiv2.waiflow.app/api/v2/leads/{lead_id}/status
```

Status flow: `new` → `contacted` → `qualified` → `converted`
(or `lost` at any stage).

### Bulk add leads to a campaign group

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_ids": ["uuid-1", "uuid-2", "uuid-3"],
    "custom_group_id": "target-group-uuid"
  }' \
  https://apiv2.waiflow.app/api/v2/leads/bulk/add-to-group
```

### Export leads as CSV

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads/export/csv?status=qualified" \
  -o qualified-leads.csv
```

### Pause a running campaign

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/pause
```

### AI reply in your writing style + knowledge base

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "5511999999999@c.us",
    "context": "Customer asks: What is your return policy?",
    "use_rag": true,
    "apply_style": true
  }' \
  https://apiv2.waiflow.app/api/v2/ai/generate-reply
```

### Schedule a weekly follow-up

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monday check-in",
    "session_id": "uuid",
    "chat_id": "123@c.us",
    "message": "Hey! Anything I can help with this week?",
    "recurrence": "weekly",
    "scheduled_time": "2026-02-17T09:00:00",
    "timezone": "America/New_York"
  }' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages
```

### Weekly report delivered to your WhatsApp

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Lead Pipeline",
    "template_id": "lead_pipeline",
    "schedule_type": "weekly",
    "cron_expression": "0 9 * * MON",
    "timezone": "America/New_York",
    "delivery_method": "whatsapp"
  }' \
  https://apiv2.waiflow.app/api/v2/reports
```

### Send a message

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "chat_id": "1234567890@c.us",
    "message": "Hello!"
  }' \
  https://apiv2.waiflow.app/api/v2/messages/send
```

### Collect customer reviews automatically

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Happy Customers",
    "session_id": "uuid",
    "source_type": "all",
    "min_sentiment_score": 0.7,
    "include_keywords": ["thank", "recommend", "love", "amazing"]
  }' \
  https://apiv2.waiflow.app/api/v2/reviews/collectors
```

### Discover A2A agents

```bash
curl https://apiv2.waiflow.app/.well-known/agent.json
```

Full API reference: see each module's SKILL.md.

---

## ERC-8004 Agent Registration

MoltFlow is a verified on-chain AI agent registered on **Ethereum mainnet**.

| Field | Value |
|-------|-------|
| Agent ID | [#25248](https://8004agents.ai/agent/25248) |
| Chain | Ethereum mainnet (eip155:1) |
| Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Trust Model | Reputation-based |
| Endpoints | A2A + MCP + Web |

**Discovery:**
- Agent card: `https://molt.waiflow.app/.well-known/erc8004-agent.json`
- A2A discovery: `https://apiv2.waiflow.app/.well-known/agent.json`

---

## Use Cases

**Solo Founder / Small Biz**
- Find unanswered leads in your chats
- AI replies in your writing style
- Scheduled promos to custom groups

**Agency / Multi-Client**
- Monitor 50+ groups across 10 sessions
- Bulk send with ban-safe delays
- Export leads as CSV, push to n8n/Zapier

**Marketing Agency / Campaign Manager**
- Capture leads from click-to-WhatsApp ad campaigns
- Auto-qualify inbound leads with keyword detection + AI scoring
- Bulk follow-up sequences with ban-safe throttling
- Multi-session management across client accounts
- Export campaign leads to CRM via webhooks or CSV

**Developer / AI Agent Builder**
- 90+ REST endpoints, scoped API keys
- A2A protocol with E2E encryption
- Python scripts for every workflow ([GitHub](https://github.com/moltflow/moltflow/tree/main/skills/moltflow-clawhub/scripts))

### Guides & Tutorials

**AI Integration Guides:**
- [Connect ChatGPT to MoltFlow](https://molt.waiflow.app/guides/connect-chatgpt-to-moltflow) — Custom GPT Actions, 10 min setup
- [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow) — MCP Server setup, 5 min
- [Connect OpenClaw to MoltFlow](https://molt.waiflow.app/guides/connect-openclaw-to-moltflow) — Native AI config, 5 min setup

**How-To Guides:**
- [Getting Started](https://molt.waiflow.app/blog/whatsapp-automation-getting-started)
- [API Complete Guide](https://molt.waiflow.app/blog/moltflow-api-complete-guide)
- [n8n Integration](https://molt.waiflow.app/blog/moltflow-n8n-whatsapp-automation)
- [n8n + Google Sheets](https://molt.waiflow.app/blog/n8n-whatsapp-google-sheets)
- [n8n Group Auto-Reply](https://molt.waiflow.app/blog/n8n-whatsapp-group-auto-reply)
- [n8n Lead Pipeline](https://molt.waiflow.app/blog/n8n-whatsapp-lead-pipeline)
- [n8n Multi-Model AI](https://molt.waiflow.app/blog/n8n-multi-model-ai-orchestration)
- [AI Auto-Replies Setup](https://molt.waiflow.app/blog/ai-auto-replies-whatsapp-setup)
- [Group Lead Generation](https://molt.waiflow.app/blog/whatsapp-group-lead-generation-guide)
- [Customer Support](https://molt.waiflow.app/blog/openclaw-whatsapp-customer-support)
- [RAG Knowledge Base](https://molt.waiflow.app/blog/rag-knowledge-base-deep-dive)
- [Style Training](https://molt.waiflow.app/blog/learn-mode-style-training-whatsapp)
- [Lead Scoring](https://molt.waiflow.app/blog/whatsapp-lead-scoring-automation)
- [Feedback Collection](https://molt.waiflow.app/blog/whatsapp-customer-feedback-collection)
- [A2A Protocol](https://molt.waiflow.app/blog/a2a-protocol-agent-communication)
- [Scaling ROI](https://molt.waiflow.app/blog/scaling-whatsapp-automation-roi)

[All guides →](https://molt.waiflow.app/guides)

---

## Platform Features

| Feature | Details |
|---|---|
| Messaging | Text, media, polls, vCards |
| Bulk Send | Ban-safe, SSE progress |
| Scheduled | Cron, timezone-aware |
| Reports | 10 templates, cron, WhatsApp delivery |
| Analytics | Campaign funnel, contact scores, send time optimization |
| Groups | Custom lists, CSV export |
| Leads/CRM | Auto-detect, pipeline |
| Monitoring | 50+ groups, keywords |
| Labels | Sync to WA Business |
| AI Replies | GPT-4/Claude, RAG |
| Style Clone | Train from your msgs |
| RAG | PDF/TXT, semantic search |
| Voice | Whisper transcription |
| Reviews | Sentiment, auto-approve |
| Anti-Spam | Rate limits, typing sim |
| Safeguards | Block PII, injections |
| Webhooks | HMAC signed, 10+ events |
| A2A | E2E encrypted, JSON-RPC |
| GDPR | Auto-expiry, compliance |
| Delivery | Real-time SSE tracking, read/reply/ignored status |

---

## How MoltFlow Compares

| | Molt | Alt 1 | Alt 2 | Alt 3 |
|---|:---:|:---:|:---:|:---:|
| Messaging | 18 | 14 | 3 | 1 |
| Groups | 8 | 4 | 0 | 0 |
| Outreach | 7 | 0 | 0 | 0 |
| CRM | 7 | 0 | 0 | 0 |
| AI | 7 | 0 | 0 | 0 |
| Reviews | 8 | 0 | 0 | 0 |
| Security | 10 | 0 | 0 | 0 |
| Platform | 8 | 0 | 0 | 0 |
| **Total** | **90+** | **~15** | **~3** | **~1** |

---

## What This Skill Reads, Writes & Never Does

**Documentation and API reference.** Nothing is
auto-installed or auto-executed. No scripts or
executables are bundled in this package.
All actions require user confirmation.

| Category | What happens | Requires opt-in? |
|---|---|---|
| API calls | HTTPS to `apiv2.waiflow.app` only | No (uses your API key) |
| Chat metadata | Contact names, timestamps, counts | No |
| Message content | 500-char previews only | Yes (chat history gate) |
| BizDev analysis | Aggregate counts, no PII | No |
| Style profiles | Statistical patterns, not raw text | Yes (AI consent) |
| Local file | `.moltflow.json` — counts only, no PII | No |
| API key | Local env var, never logged or shared | No |

**This skill never:**
- Installs packages or runs code automatically
- Reads full message content without tenant opt-in
- Sends messages without explicit user confirmation
- Sends to non-whitelisted numbers (if configured)
- Bypasses anti-spam or content safeguards
- Shares data with third parties
- Stores credentials in files (env vars only)

---

## Setup

> **Free tier available** — 1 session,
> 50 messages/month, no credit card required.

**Env vars:**
- `MOLTFLOW_API_KEY` (required) — from
  [your dashboard](https://molt.waiflow.app)
- `MOLTFLOW_API_URL` (optional) — defaults
  to `https://apiv2.waiflow.app`

**Authentication:**
`X-API-Key: $MOLTFLOW_API_KEY` header
or `Authorization: Bearer $TOKEN` (JWT).

**Base URL:** `https://apiv2.waiflow.app/api/v2`

---

## Security

- **Scoped API keys enforced** — `scopes` is a
  required field when creating keys. Select only
  the permissions you need (e.g., `messages:send`,
  `leads:read`). Use presets like "Messaging" or
  "Outreach" for common workflows.
- **Chat history requires explicit opt-in** — the
  API enforces a consent gate. Features like
  "scan my chats" or style training will fail
  unless you enable access at Dashboard >
  Settings > Account > Data Access first.
  Disabled by default for GDPR compliance.
- **Use environment variables for keys** — set
  `MOLTFLOW_API_KEY` as an env var, not in
  shared config files. Rotate keys regularly.
- **Phone whitelisting** — configure `allowed_numbers`
  in tenant settings to restrict which numbers can
  send outbound messages. Only whitelisted numbers
  are permitted.
- **Anti-spam safeguards** — all outbound messages
  pass through reciprocity checks (contact must
  message you first), burst rate limiting, typing
  simulation, and random delays. Cannot be bypassed.
- **Content safeguards** — outbound messages are
  scanned for PII, secrets, and prompt injection
  attempts. Blocked automatically before sending.
- **Approval mode** — enable `require_approval` in
  tenant settings to hold all AI-generated messages
  for manual review before delivery.
- **Webhook URL validation** — the API blocks
  private IPs, cloud metadata, and non-HTTPS
  schemes. Only configure endpoints you control.
  Always set a `secret` for HMAC verification
- **Verify third-party packages before running** —
  if you follow the external setup guides to install
  MCP or GPT integrations, review the package source
  and maintainers first. This skill does not install
  or execute any packages.
- **Review scripts locally before running** — the
  Python example scripts are hosted on GitHub, not
  bundled. Download, inspect the source, then run.
- **Avoid high-privilege keys in shared environments** —
  for admin operations (key rotation, data export),
  use the browser dashboard or a short-lived scoped
  key. Never expose owner-level keys in shared shells.
- **Test in a sandbox tenant first** — create a
  short-lived, scoped key for testing. Revoke
  after testing. Never share keys across tenants.

---

## AI Agent Integrations

25 MCP tools for Claude Desktop, Claude.ai,
Claude Code, and OpenAI Custom GPTs.

**User Action Required** — each integration
requires manual setup by the user. No code
is installed automatically by this skill.

See [integrations.md](integrations.md) for setup
guides and security notes.

---

## Modules

Each module has its own SKILL.md with endpoints
and curl examples.

- **moltflow** (Core) — sessions, messaging,
  groups, labels, webhooks
- **moltflow-outreach** — bulk send,
  scheduled messages, scheduled reports, custom groups
- **moltflow-ai** — style cloning, RAG,
  voice transcription, AI replies
- **moltflow-leads** — lead detection,
  CRM pipeline, bulk ops, export
- **moltflow-a2a** — agent-to-agent protocol,
  encrypted messaging
- **moltflow-reviews** — review collection,
  sentiment analysis, testimonial export
- **moltflow-admin** — auth, API keys,
  billing, usage tracking
- **moltflow-onboarding** — BizDev growth agent,
  on-demand account analysis, opportunity discovery

---

## Notes

- Anti-spam on all messages (typing, random delays)
- Sessions require QR code pairing on first connect
- Use E.164 phone format without `+`
- AI features and A2A require Pro plan or above
- Rate limits: Free 10, Starter 20, Pro 40, Biz 60/min

---

## Changelog

**v2.11.3** (2026-02-15) -- See [CHANGELOG.md](CHANGELOG.md) for full history.

<!-- FILEMAP:BEGIN -->
```text
[moltflow file map]|root: .
|.:{SKILL.md,CHANGELOG.md,integrations.md,package.json}
|moltflow:{SKILL.md}
|moltflow-ai:{SKILL.md}
|moltflow-a2a:{SKILL.md}
|moltflow-reviews:{SKILL.md}
|moltflow-outreach:{SKILL.md}
|moltflow-leads:{SKILL.md}
|moltflow-admin:{SKILL.md}
|moltflow-onboarding:{SKILL.md}
```
<!-- FILEMAP:END -->
