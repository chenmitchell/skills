---
name: memento
description: Local persistent memory for OpenClaw agents. Captures conversations, extracts structured facts via LLM, and auto-recalls relevant knowledge before each turn. Privacy-first, all stored data stays local in SQLite.
metadata:
  version: "0.3.2"
  author: braibaud
  license: MIT
  repository: https://github.com/braibaud/Memento
  openclaw:
    emoji: "🧠"
    kind: plugin
    requires:
      node: ">=18.0.0"
      env:
        - ANTHROPIC_API_KEY
        - OPENAI_API_KEY
        - MISTRAL_API_KEY
        - MEMENTO_API_KEY
        - MEMENTO_WORKSPACE_MAIN
      config:
        - "~/.engram/conversations.sqlite"
        - "~/.engram/migration-config.json"
    install:
      - id: npm
        kind: node
        package: "@openclaw/memento"
        label: "Install Memento plugin (npm)"
    extensions:
      - "./src/index.ts"
  keywords:
    - memory
    - knowledge-base
    - recall
    - conversation
    - extraction
    - embeddings
    - sqlite
    - privacy
    - local
    - cross-agent
---

# Memento — Local Persistent Memory for OpenClaw Agents

Memento gives your agents long-term memory. It captures conversations, extracts structured facts using an LLM, and auto-injects relevant knowledge before each AI turn.

**All stored data stays on your machine — no cloud sync, no subscriptions.** Extraction uses your configured LLM provider; use a local model (Ollama) for fully air-gapped operation.

> ⚠️ **Privacy note:** When `autoExtract` is enabled, conversation segments are sent to your configured LLM provider for fact extraction. If you use a cloud provider (Anthropic, OpenAI, Mistral), that text leaves your machine. For fully local operation, set `extractionModel` to `ollama/<model>` and keep Ollama running locally.

## What It Does

1. **Captures** every conversation turn, buffered per session
2. **Extracts** structured facts (preferences, decisions, people, action items) via configurable LLM (opt-in — see Privacy section)
3. **Recalls** relevant facts before each AI turn using FTS5 keyword search + optional semantic embeddings (BGE-M3)
4. **Respects privacy** — facts are classified as `shared`, `private`, or `secret` based on content, with hard overrides for sensitive categories (medical, financial, credentials)
5. **Cross-agent knowledge** — shared facts flow between agents with provenance tags; private/secret facts never cross boundaries

## Quick Start

Install the plugin, restart your gateway, and Memento starts capturing automatically. Extraction is **off by default** — enable it explicitly when ready.

### Optional: Semantic Search

Download a local embedding model for richer recall:

```bash
mkdir -p ~/.node-llama-cpp/models
curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf \
  "https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"
```

## Environment Variables

All environment variables are **optional** — you only need the one matching your chosen LLM provider:

| Variable | When Needed |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Using `anthropic/*` models for extraction |
| `OPENAI_API_KEY` | Using `openai/*` models for extraction |
| `MISTRAL_API_KEY` | Using `mistral/*` models for extraction |
| `MEMENTO_API_KEY` | Generic fallback for any provider |
| `MEMENTO_WORKSPACE_MAIN` | Migration only: path to agent workspace for bootstrapping |

No API key needed for `ollama/*` models (local inference).

## Configuration

Add to your `openclaw.json` under `plugins.entries.memento.config`:

```json
{
  "memento": {
    "autoCapture": true,
    "extractionModel": "anthropic/claude-sonnet-4-6",
    "extraction": {
      "autoExtract": true,
      "minTurnsForExtraction": 3
    },
    "recall": {
      "autoRecall": true,
      "maxFacts": 20,
      "crossAgentRecall": true
    }
  }
}
```

> **`autoExtract: true`** is an explicit opt-in (default: `false`). When enabled, conversation segments are sent to the configured `extractionModel` for LLM-based fact extraction. Omit or set to `false` to keep everything local.

## Data Storage

Memento stores all data locally:

| Path | Contents |
|------|----------|
| `~/.engram/conversations.sqlite` | Main database: conversations, facts, embeddings |
| `~/.engram/segments/*.jsonl` | Human-readable conversation backups |
| `~/.engram/migration-config.json` | Optional: migration workspace paths (only for bootstrapping) |

The `~/.engram` directory name is a legacy from when the project was called Engram. It will not change to avoid breaking existing installations.

## Privacy & Data Flow

| Feature | Data leaves machine? | Details |
|---------|---------------------|---------|
| `autoCapture` (default: `true`) | ❌ No | Writes to local SQLite + JSONL only |
| `autoExtract` (default: `false`) | ⚠️ Yes, if cloud LLM | Sends conversation text to configured provider. Use `ollama/*` for local. |
| `autoRecall` (default: `true`) | ❌ No | Reads from local SQLite only |
| Secret facts | ❌ Never | Filtered from extraction context — never sent to any LLM |
| Migration | ❌ No | Reads local workspace files, writes to local SQLite |

## Migration (Bootstrap from Existing Memory Files)

To bootstrap Memento from existing agent memory files:

1. Create `~/.engram/migration-config.json` or set `MEMENTO_WORKSPACE_MAIN`:

```json
{
  "agents": [
    {
      "agentId": "main",
      "workspace": "/path/to/your-workspace",
      "paths": ["MEMORY.md", "memory/*.md"]
    }
  ]
}
```

2. **Always dry-run first** to verify which files will be read:

```bash
npx tsx src/extraction/migrate.ts --all --dry-run
```

3. Run the actual migration:

```bash
npx tsx src/extraction/migrate.ts --all
```

⚠️ Migration reads files from the workspace paths you specify. Review the config before running.

## Architecture

- **Capture layer** — hooks `message:received` + `message:sent`, buffers multi-turn segments
- **Extraction layer** — async LLM extraction with deduplication, occurrence tracking, and temporal pattern detection
- **Storage layer** — SQLite (better-sqlite3) with FTS5 full-text search + optional vector embeddings
- **Recall layer** — multi-factor scoring (recency × frequency × category weight) injected via `before_prompt_build` hook

## Requirements

- OpenClaw 2026.2.20+
- Node.js 18+
- An API key for your preferred LLM provider (for extraction — not needed if extraction is disabled or using Ollama)
- Optional: GPU for accelerated embedding search (falls back to CPU gracefully)

## Install

```bash
# From ClawHub
clawhub install memento

# Or for local development
git clone https://github.com/braibaud/Memento
cd Memento
npm install
```

Note: `better-sqlite3` includes native bindings that compile during `npm install`. This is expected behavior for SQLite access.
