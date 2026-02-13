# AI Sentinel — OpenClaw Plugin

Prompt injection detection and security scanning for [OpenClaw](https://openclaw.com) agents. Scans messages, tool results, and tool parameters in real time using 39 regex-based threat patterns across 8 categories.

## Install

```bash
openclaw plugins install openclaw-ai-sentinel
```

Or via npm directly:

```bash
npm install openclaw-ai-sentinel
```

## Configuration

Add to your `~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "ai-sentinel": {
        enabled: true,
        config: {
          mode: "monitor",           // "monitor" | "enforce"
          threatThreshold: 0.7,      // 0.0–1.0, block above this in enforce mode
          logLevel: "info",          // "debug" | "info" | "warn" | "error"
          allowlist: [],             // session keys to skip scanning
        },
      },
    },
  },
}
```

### Modes

| Mode | Behavior |
|------|----------|
| `monitor` | Log threats and annotate the transcript, but allow messages through |
| `enforce` | Block messages above `threatThreshold` and return a safety notice |

### Cloud Reporting (optional)

Connect to AI Sentinel Pro for dashboards, threat intel feeds, and alerting:

```json5
{
  config: {
    apiKey: "sk-...",               // or set AI_SENTINEL_API_KEY env var
    apiUrl: "https://api.zetro.ai",
    reportMode: "telemetry",        // "telemetry" | "cloud-scan" | "none"
    reportFilter: "all",            // "all" | "threats-only"
  },
}
```

### Multi-Agent Support

Configure per-agent scanning behavior:

```json5
{
  config: {
    agentId: "my-agent",
    excludeAgents: ["internal-bot"],
    agentOverrides: [
      { agentId: "high-risk-agent", mode: "enforce", threatThreshold: 0.5 }
    ],
  },
}
```

## What It Detects

39 patterns across 8 threat categories:

| Category | Patterns | Examples |
|----------|----------|---------|
| Prompt Injection | PI-001 – PI-006 | "ignore previous instructions", chat template delimiters |
| Jailbreak | JB-001 – JB-009 | DAN, developer mode, character override, bracket persona |
| Instruction Override | IO-001 – IO-003 | "forget everything", "override your safety" |
| Data Exfiltration | DE-001 – DE-007 | "repeat words above", "paste your system prompt" |
| Social Engineering | SE-001 – SE-005 | False authority claims, fake security audits |
| Tool Abuse | TA-001 – TA-003 | Code execution injection, pipe-to-shell |
| Indirect Injection | II-001 – II-005 | Hidden instructions in documents, zero-width chars |

Tool results get an automatic confidence boost (+0.15) since indirect injection is higher-signal in untrusted content.

## How It Works

AI Sentinel registers hooks into the OpenClaw plugin lifecycle:

| Hook | Purpose |
|------|---------|
| `message_received` | Scan inbound user messages before the agent processes them |
| `tool_result_persist` | Scan tool results for indirect prompt injection |
| `before_tool_call` | Inspect tool parameters before execution |
| `before_agent_start` | Inject security awareness into the agent's system prompt |

It also registers an `ai_sentinel_scan` tool that agents can call to manually scan suspicious content.

## Bootstrap Hook (standalone)

For an additional layer of defense, install the gateway bootstrap hook which injects security awareness rules into the agent's system prompt at startup:

```bash
./scripts/install-bootstrap-hook.sh
openclaw hooks enable ai-sentinel-bootstrap
```

## Development

```bash
npm run build          # Compile TypeScript
npm run test           # Run 99 tests (pattern coverage + promptmap corpus + scan engine)
npm run dev            # Watch mode
npm run typecheck      # Type-check without emitting
```

## License

MIT
