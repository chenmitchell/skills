# Changelog

All notable changes to the **MoltFlow Skills** package are documented here.

---

## v2.11.3 (2026-02-15)

### Fixed
- Reverted Setup and Security sections to v2.10.2 wording for ClawHub review compatibility

## v2.11.0 (2026-02-15)

### Added
- **ERC-8004 Agent Registration** — MoltFlow registered as Agent #25248 on Ethereum mainnet
- ERC-8004 section in SKILL.md with registry details and discovery URLs
- New keywords: `erc8004`, `ethereum-agent`, `on-chain-agent`

---

## v2.10.1 (2026-02-14)

### Added
- **New code samples** — CRM pipeline updates, bulk group operations, CSV export, campaign controls
- **Delivery tracking** added to Platform Features table
- **Comparison table** total updated to 90+ endpoints

### Changed
- Removed scripts section (scripts will move to dedicated repo)

---

## v2.9.8 (2026-02-14)

### Changed
- **Integrations.md cleaned up** — simplified to setup guide links and security notes only
- **Changelog consolidated** — removed verbose patch-level entries

### Security
- **Documentation-only package** — zero executables, zero install scripts, zero local file writes
- **Scoped API keys enforced** — all examples use minimum required scopes; wildcard keys never recommended
- **Chat history gated** — API returns HTTP 403 until tenant explicitly opts in at Settings > Account > Data Access
- **High-privilege endpoints removed from skill docs** — only consumer-facing API endpoints documented; administrative operations available on website only
- **Model invocation disabled** — `disable-model-invocation: true` prevents autonomous agent actions; all operations require explicit user invocation
- **Anti-spam safeguards documented** — reciprocity checks, burst rate limits, and content safeguards apply to all outbound messages

---

## v2.9.7 (2026-02-14)

### Changed
- **Code samples reordered** — campaign analytics, real-time delivery tracking (SSE), and engagement leaderboard moved to top of main SKILL.md
- **Admin skill streamlined** — focused on auth, API keys, billing, usage, and tenant settings
- **Restored integrations.md** — clean version with setup guide links and security notes

---

## v2.9.0 (2026-02-14)

### Added
- Campaign analytics endpoints documentation (Pro+ plans)
- Contact engagement scoring and leaderboard
- Send time optimization heatmap
- 3 new MCP tools for analytics

### Changed
- Display name updated for search discoverability
- Documentation refined for security best practices
- All marketing language clarified for accuracy
- Package reduced to documentation-only (zero executables)

---

## v2.8.6 (2026-02-14)

### Changed
- **Least-privilege API keys** — `scopes` is now required when creating API keys; presets available (Messaging, Outreach, Read Only)
- **403 errors include required scopes** — `X-Required-Scopes` header tells callers exactly which scopes they need

---

## v2.8.0 (2026-02-13)

### Added
- **Scheduled Reports** — 10 report templates with WhatsApp delivery support
- Reports API (8 endpoints): templates, create, list, get, update, pause, resume, delete
- `reports:read` and `reports:manage` scopes

### Changed
- Platform features table updated with reports
- Outreach module now includes scheduled reports

---

## v2.7.0 (2026-02-13)

### Changed
- Documentation restructured for clarity — "What This Skill Reads, Writes & Never Does" section
- Privacy documentation expanded with opt-in requirements and explicit "never does" list
- Security section expanded — anti-spam safeguards, content safeguards, approval mode

---

## v2.4.0 (2026-02-13)

### Added
- **AI Agent Integrations** — setup guides for Claude Desktop, Claude.ai Web, Claude Code, and ChatGPT
- Remote MCP gateway documentation (`apiv2.waiflow.app/mcp`)

---

## v2.0.0 (2026-02-12)

### Highlights

- **Scheduled Messages** — One-time, daily/weekly/monthly, or custom cron. Timezone-aware. Pause, resume, cancel. Full execution history.
- **Bulk Messaging** — Broadcast to custom groups with ban-safe throttling. Real-time SSE progress. Pause/resume/cancel mid-flight.
- **Custom Groups** — Build targeted contact lists from WhatsApp conversations. Import members, export CSV/JSON.
- **Lead Management** — Auto-detected leads with full pipeline tracking. Bulk operations, CSV/JSON export.
- **Knowledge Base (RAG)** — Upload PDF/TXT, semantic search with embeddings. AI uses your docs for accurate answers.
- **Voice Transcription** — Whisper-powered voice message transcription with async task queue.
- **90+ API Endpoints** — Complete platform coverage across 6 modules.

### Added

- Scheduled Messages API (9 endpoints)
- Bulk Send API (7 endpoints)
- Custom Groups API (10 endpoints)
- Leads API (8 endpoints)
- Knowledge Base / RAG API (4 endpoints)
- Voice Transcription API (3 endpoints)
- Sub-skills: moltflow-outreach, moltflow-leads, moltflow-admin

---

## v1.6.0 (2026-02-11)

### Highlights

- **Anti-Spam Protection** — Reciprocity checks, burst rate limiting, and health monitoring on all outbound messages.
- **Yearly Billing** — Lock in yearly pricing at $239.90/year.
- **4 Focused Sub-Skills** — Core, AI, A2A, and Reviews modules.

---

## v1.0.0 (2026-02-06)

### Highlights

- **All-in-One WhatsApp API** — Sessions, messaging, groups, labels, webhooks, AI replies, reviews, and A2A unified under a single skill.
- **Agent-to-Agent Protocol** — JSON-RPC 2.0 with end-to-end encryption.
- **AI That Learns Your Voice** — Train style profiles from message history. Auto-replies sound like you.
- Full API reference with curl examples across 6 modules.

---

*Built with care by the [MoltFlow](https://waiflow.app) team.*
