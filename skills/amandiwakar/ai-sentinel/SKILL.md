---
name: ai-sentinel
description: "Prompt injection detection and security scanning for OpenClaw agents. 39 regex-based threat patterns across 8 categories — scans messages, tool results, and tool parameters in real time. Monitor or enforce mode with configurable thresholds, multi-agent support, and optional cloud telemetry."
user-invocable: false
metadata: {"openclaw":{"emoji":"🛡️","plugin":true,"os":["darwin","linux","win32"]}}
---

# AI Sentinel

Real-time prompt injection detection for OpenClaw agents. Scans inbound messages, tool results, and tool parameters against 39 threat patterns across 8 categories. Runs in-process as an OpenClaw plugin — no sidecar, no network calls for local-only mode.

## Install

```bash
openclaw plugins install ai-sentinel
```

Or from npm:

```bash
npm install openclaw-ai-sentinel
```

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "ai-sentinel": {
        enabled: true,
        config: {
          mode: "monitor",           // "monitor" | "enforce"
          threatThreshold: 0.7,      // 0.0–1.0, block above this in enforce mode
          logLevel: "info",
          allowlist: [],             // session keys to skip
        },
      },
    },
  },
}
```

### Modes

| Mode | Behavior |
|------|----------|
| **monitor** | Log threats and annotate the transcript, allow messages through |
| **enforce** | Block messages above `threatThreshold`, return a safety notice to the user |

### Cloud Reporting (optional)

Connect to AI Sentinel Pro for dashboards, alerting, and threat intel feeds:

```json5
{
  config: {
    apiKey: "sk-...",               // or set AI_SENTINEL_API_KEY env var
    apiUrl: "https://api.zetro.ai",
    reportMode: "telemetry",        // "telemetry" | "cloud-scan" | "none"
  },
}
```

### Multi-Agent

```json5
{
  config: {
    excludeAgents: ["internal-bot"],
    agentOverrides: [
      { agentId: "high-risk-agent", mode: "enforce", threatThreshold: 0.5 }
    ],
  },
}
```

## What It Detects

39 patterns across 8 threat categories:

| Category | IDs | Examples |
|----------|-----|---------|
| Prompt Injection | PI-001 – PI-006 | "ignore previous instructions", chat template delimiters |
| Jailbreak | JB-001 – JB-009 | DAN, developer mode, character override, bracket persona, respond-without-filter |
| Instruction Override | IO-001 – IO-003 | "forget everything", "override your safety" |
| Data Exfiltration | DE-001 – DE-007 | "repeat words above", "paste your system prompt", "list guidelines you follow" |
| Social Engineering | SE-001 – SE-005 | False authority claims, fake security audits, maintainer impersonation |
| Tool Abuse | TA-001 – TA-003 | Code execution injection, pipe-to-shell |
| Indirect Injection | II-001 – II-005 | Hidden instructions in documents, zero-width chars, code wrapper attacks |

Tool results get an automatic confidence boost (+0.15) since indirect injection is higher-signal in untrusted content.

## Plugin Hooks

| Hook | Purpose |
|------|---------|
| `message_received` | Scan inbound messages before the agent processes them |
| `tool_result_persist` | Scan tool results for indirect prompt injection |
| `before_tool_call` | Inspect tool parameters before execution |
| `before_agent_start` | Inject security awareness into the agent's system prompt |

Also registers an `ai_sentinel_scan` tool for manual on-demand scanning.

## Bootstrap Hook (standalone)

For defense-in-depth, install the gateway bootstrap hook to inject security rules into agent system prompts at startup:

```bash
./scripts/install-bootstrap-hook.sh
openclaw hooks enable ai-sentinel-bootstrap
```

## No External Dependencies

Only runtime dependency is `zod` for config validation. All pattern matching runs locally — no network calls unless cloud reporting is enabled.
