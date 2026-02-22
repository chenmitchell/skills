# Distil — OpenClaw Native Skill

This directory contains the **Distil native skill for [OpenClaw](https://openclaw.ai)** — gives AI agents running inside OpenClaw direct, zero-configuration access to the Distil web proxy.

## What's in this folder

| File | Description |
|------|-------------|
| `SKILL.md` | OpenClaw skill manifest — describes the skill to OpenClaw and documents commands for the agent |

## How it works

When OpenClaw discovers this skill, it:

1. Reads `SKILL.md` to learn the skill name, description, and what commands are available
2. Installs the `distil-proxy` npm package (or prompts you to do so)
3. The agent can then call `distil fetch <URL>` or `distil search <query>` directly from shell commands

The distil-proxy server can be found at [https://www.npmjs.com/package/distil-proxy](https://www.npmjs.com/package/distil-proxy) with github package located at [https://github.com/exec-io/distil-proxy](https://github.com/exec-io/distil-proxy)

## Installation

```bash
npm install -g distil-proxy
```

Set the `DISTIL_API_KEY` environment variable to your key from [distil.net](https://distil.net).

### Verify the install

```bash
distil fetch https://example.com
```

You should get clean Markdown back. If you see an error about a missing API key, set the `DISTIL_API_KEY` environment variable.

## Usage

```bash
# Fetch any URL as clean Markdown
distil fetch https://example.com

# Search the web and get results as Markdown
distil search "best practices for Go error handling"

# Multi-word queries work naturally — no quoting needed
distil search top 10 AI companies 2025

# Screenshot a page
distil screenshot https://example.com

# Render a javascript SPA before extracting markdown
distil render https://example.com

# Get raw content without markdown conversion
distil raw https://example.com

# Bypass cache
distil nocache https://news.ycombinator.com
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DISTIL_API_KEY` | (required) | Your Distil API key |
| `DISTIL_PROXY_URL` | `https://proxy.distil.net` | Proxy base URL — override for self-hosted instances |

## Output

- **`distil fetch`** — page content as clean Markdown on stdout, HTTP errors on stderr
- **`distil search`** — search results (titles, URLs, descriptions) as Markdown on stdout
- **Exit codes** — `0` on success, `1` on any error (missing key, HTTP failure, bad usage)

## Getting an API key

Sign up at [distil.net](https://distil.net) — free tier included.

Your key looks like `dk_yourkey`. Set it as an environment variable:

```bash
export DISTIL_API_KEY=dk_yourkey
```

## Troubleshooting

**"DISTIL_API_KEY environment variable is required"** — set `DISTIL_API_KEY=dk_yourkey` in your shell or MCP config

**"fetch failed"** — verify your key is valid at [distil.net/usage](https://distil.net/usage); check connectivity with `curl -s https://proxy.distil.net/healthz`

**Empty output** — the page may require JavaScript rendering; try `distil render` instead of `distil fetch`
