---
name: cascadeflow
description: Set up CascadeFlow as an OpenClaw custom provider with fast, copy-paste steps. Use when users want quick install, preset selection (OpenAI-only, Anthropic-only, mixed), OpenClaw model alias setup, and safe production defaults for cascading with streaming and agent loops.
---

# CascadeFlow: Cost + Latency Reduction

Use CascadeFlow as an OpenClaw provider to lower cost and latency via cascading.
Keep setup minimal, then verify with one health check and one chat call.

## Fast Start

1. Install:
```bash
git clone https://github.com/lemony-ai/cascadeflow.git
cd cascadeflow
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[openclaw,providers]"
```

2. Choose one preset:
- `examples/configs/anthropic-only.yaml`
- `examples/configs/openai-only.yaml`
- `examples/configs/mixed-anthropic-openai.yaml`

3. Add keys in `.env`:
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

4. Start server:
```bash
set -a; source .env; set +a
python3 -m cascadeflow.integrations.openclaw.openai_server \
  --host 127.0.0.1 \
  --port 8084 \
  --config examples/configs/anthropic-only.yaml \
  --auth-token local-openclaw-token \
  --stats-auth-token local-stats-token
```

5. Configure OpenClaw provider:
- `baseUrl`: `http://127.0.0.1:8084/v1`
- `api`: `openai-completions`
- `model`: `cascadeflow`

6. Add alias and use it:
- Set alias `cflow` for `cascadeflow/cascadeflow` in OpenClaw config.
- Switch with `/model cflow`.
- Treat `/cascade` as optional custom command only if configured in OpenClaw.

## What Users Get

- Cost/latency reduction via cascading.
- Support for cascading while streaming is enabled.
- Support for cascading in multi-step agent loops.
- OpenAI-compatible `/v1/chat/completions` transport for OpenClaw.
- Domain-aware cascading via model presets.

## Safe Defaults

- Bind local: `127.0.0.1`.
- Use auth tokens for API and stats.
- Keep external exposure behind TLS reverse proxy.

## Full Docs

- `references/clawhub_publish_pack.md` for complete config and validation.
- `references/market_positioning.md` for listing copy and positioning.
