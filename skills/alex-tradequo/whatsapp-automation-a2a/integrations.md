# AI Agent Integrations

> **User Action Required.** Each integration below
> requires manual setup outside this skill. This skill
> does not install packages or run code.

MoltFlow works as a tool provider for AI assistants.
Connect your preferred AI platform to the MoltFlow API
and manage WhatsApp directly from conversation.

## Claude Desktop (MCP Server)

25 MCP tools for sessions, messaging, groups, leads,
outreach, and usage.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

**Required scopes:** Use the minimum scopes for your
workflow: `sessions:read`, `messages:send`, `leads:read`,
`custom-groups:read`, `usage:read`. Create a scoped key
at Dashboard > Settings > API Keys.

## Claude.ai Web (Remote MCP)

No installation required — MoltFlow hosts a remote MCP
gateway. Configure in Claude.ai under Settings >
Integrations > MCP Servers:

- **URL:** `https://apiv2.waiflow.app/mcp`
- **Auth header:** `X-API-Key`
- **Value:** Your scoped MoltFlow API key

All 25 tools are available immediately after configuration.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

## Claude Code

Guided skills and MCP tools for Claude Code.

**Setup guide:** [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow)

Available skills: `send-message`, `list-sessions`,
`check-leads`, `bulk-send`, `help`.

Set `MOLTFLOW_API_KEY` in your environment before launching.

## OpenAI Custom GPTs (ChatGPT)

Import the MoltFlow OpenAPI specification in GPT Builder
to give your GPT access to messaging, sessions, leads,
and outreach endpoints.

**Setup guide:** [Connect ChatGPT to MoltFlow](https://molt.waiflow.app/guides/connect-chatgpt-to-moltflow)

Set Authentication to "API Key" with header `X-API-Key`
and paste your scoped MoltFlow API key.

---

## Security Notes

- **Scoped API keys only** — create a key with minimum
  required scopes at Dashboard > Settings > API Keys.
- **Environment variables** — store your API key as an
  env var, not in shared config files. Rotate regularly.
- **Chat history gate** — chat reading endpoints require
  explicit tenant opt-in at Settings > Account > Data
  Access. Disabled by default for GDPR compliance.

---

## A2A Discovery (ERC-8004)

MoltFlow is registered as [Agent #25248](https://8004agents.ai/agent/25248) on Ethereum mainnet.

Other AI agents can discover MoltFlow through:

- **On-chain**: Query ERC-8004 Identity Registry at `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- **HTTP**: Fetch `https://apiv2.waiflow.app/.well-known/agent.json`
- **Agent card**: `https://molt.waiflow.app/.well-known/erc8004-agent.json`
