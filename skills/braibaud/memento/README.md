# Memento — Local Persistent Memory for OpenClaw Agents

**Memento** gives OpenClaw agents a long-term memory — structured, private, and stored entirely on your machine. All stored data stays local — no cloud sync, no subscriptions. Extraction uses your configured LLM provider; use a local model (Ollama) for fully air-gapped operation.

> ⚠️ **Privacy note:** When `autoExtract` is enabled, conversation segments are sent to your configured LLM provider for fact extraction. If you use a cloud provider (Anthropic, OpenAI, Mistral), that text leaves your machine. For fully local operation, set `extractionModel` to `ollama/<model>`.

---

## Features

- **📥 Capture** — buffers every conversation turn per session, auto-flushes on pause or session end
- **🧠 Extraction** — asynchronously extracts structured facts (preferences, decisions, people, etc.) using the configured LLM
- **🔍 Recall** — injects relevant facts before each AI turn via FTS5 keyword search + optional semantic embedding search
- **🔒 Privacy-first** — facts are classified by visibility (`shared` / `private` / `secret`); secret facts never leave your machine or cross agent boundaries
- **🌐 Cross-agent KB** — shared facts from multiple agents are surfaced with provenance tags in recall
- **📊 Temporal intelligence** — recency, frequency, and category weights govern recall ranking

---

## Architecture

```
                ┌─────────────────────────────────────────────────────────────┐
                │                      OpenClaw Agent                         │
                │                                                             │
  Conversation  │   message_received ──► ConversationBuffer ──► SegmentWriter │
  Flow          │                                                    │         │
                │                                          ExtractionTrigger  │
                │                                                    │         │
                │                                          extractFacts (LLM) │
                │                                                    │         │
                │                                          processExtractedFacts│
                │                                                    │         │
                │                                             SQLite facts DB  │
                │                                                             │
  Recall        │   before_prompt_build ──► searchRelevantFacts ──► inject   │
                └─────────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Description |
|--------|-------------|
| `src/index.ts` | Plugin entry point — registers hooks and services |
| `src/capture/buffer.ts` | In-memory session buffer with auto-flush |
| `src/capture/writer.ts` | Persists segments to SQLite + JSONL |
| `src/extraction/extractor.ts` | LLM-based fact extraction (provider-agnostic: Anthropic, OpenAI, Mistral, Ollama) |
| `src/extraction/deduplicator.ts` | Dedup / supersede / insert logic |
| `src/extraction/trigger.ts` | Async extraction scheduling with rate limiting |
| `src/extraction/classifier.ts` | Visibility classification with hard overrides |
| `src/recall/search.ts` | FTS5 + semantic search with multi-factor scoring |
| `src/recall/context-builder.ts` | Formats recalled facts for injection |
| `src/storage/db.ts` | SQLite database layer (better-sqlite3) |
| `src/storage/embeddings.ts` | Local embedding engine via node-llama-cpp |
| `src/storage/schema.ts` | SQLite schema, migrations, row types |
| `src/config.ts` | Plugin configuration with defaults |
| `src/types.ts` | Shared TypeScript types |

---

## Installation

Memento is a plugin for OpenClaw. Install it from the plugin directory:

```bash
openclaw plugin install @openclaw/memento
```

Or for local development, clone and link:

```bash
git clone https://github.com/openclaw/memento
cd memento
npm install
npm link
openclaw plugin link /path/to/memento
```

---

## Configuration

Add to your `openclaw.json` under `plugins.entries.memento.config`:

> **`extractionModel`** accepts any of these provider prefixes:
> `anthropic/` · `openai/` · `mistral/` · `ollama/` (or any OpenAI-compatible string as fallback).
> Set the matching API key env var: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MISTRAL_API_KEY`.
> Ollama runs locally — no key needed.

```json
{
  "memento": {
    "autoCapture": true,
    "dataDir": ".engram",
    "extractionModel": "anthropic/claude-sonnet-4-6",
    "embeddingModel": "hf:BAAI/bge-m3-gguf",
    "agentDisplay": {
      "main": "Main Assistant",
      "medbot": "Medical Bot"
    },
    "extraction": {
      "autoExtract": true,
      "minTurnsForExtraction": 3,
      "maxExtractionsPerMinute": 10,
      "includeExistingFactsCount": 50
    },
    "recall": {
      "autoRecall": true,
      "maxFacts": 20,
      "maxContextChars": 4000,
      "minQueryLength": 5,
      "crossAgentRecall": true
    }
  }
}
```

> **`autoExtract: true`** is an explicit opt-in (default: `false`). When enabled, conversation segments are sent to the configured `extractionModel` for LLM-based fact extraction. Omit or set to `false` to keep everything local (capture + recall still work via SQLite without any LLM calls).

### Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `autoCapture` | `true` | Buffer and persist all conversation messages |
| `dataDir` | `.engram` | Data directory (relative to workspace) |
| `extractionModel` | `anthropic/claude-sonnet-4-6` | LLM for fact extraction — supports `anthropic/`, `openai/`, `mistral/`, `ollama/` prefixes |
| `embeddingModel` | `hf:BAAI/bge-m3-gguf` | Local embedding model (HuggingFace URI or path) |
| `agentDisplay` | `{}` | Human-readable names for agents in cross-agent recall tags |
| `extraction.autoExtract` | `false` | **Opt-in**: automatically extract facts after each segment — sends conversation text to the configured LLM provider |
| `extraction.minTurnsForExtraction` | `3` | Skip very short segments |
| `extraction.maxExtractionsPerMinute` | `10` | Rate limit for LLM calls |
| `recall.autoRecall` | `true` | Inject relevant facts before each AI turn |
| `recall.maxFacts` | `20` | Maximum facts to inject per turn |
| `recall.maxContextChars` | `4000` | Maximum characters for the injected context block |
| `recall.crossAgentRecall` | `true` | Include shared facts from other agents |

---

## Local Development Setup

### Prerequisites

- Node.js 18+
- TypeScript 5.7+
- OpenClaw installed globally

### TypeScript path resolution

The `openclaw/plugin-sdk` module type declarations are resolved from the OpenClaw installation. After cloning:

```bash
# Option 1: npm link (recommended for local dev)
npm link openclaw

# Option 2: adjust tsconfig.json paths to point to your global install
# $(npm root -g)/openclaw/dist/plugin-sdk/index.d.ts
```

### Type-check

```bash
npx tsc --noEmit
```

---

## Fact Migration (Bootstrap from Existing Memory Files)

To bootstrap Memento's knowledge base from existing agent workspace memory files.

> **Tip:** Always run with `--dry-run` first to preview what will be imported without making any writes. Migration reads files from the workspace paths you specify — make sure paths are correct before committing.

1. Create `~/.engram/migration-config.json`:

```json
{
  "agents": [
    {
      "agentId": "main",
      "workspace": "/home/yourname/your-workspace",
      "paths": ["MEMORY.md", "memory/*.md"]
    }
  ]
}
```

Or set `MEMENTO_WORKSPACE_MAIN` environment variable.

2. Run the migration:

```bash
# Dry run (no writes)
npx tsx src/extraction/migrate.ts --all --dry-run

# Process all agents
npx tsx src/extraction/migrate.ts --all

# Single agent
npx tsx src/extraction/migrate.ts --agent main
```

---

## Privacy & Security

| Feature | Data location | Leaves your machine? |
|---------|--------------|----------------------|
| `autoCapture: true` | SQLite + JSONL on disk | ❌ Never |
| `autoExtract: true` | Sends conversation segments to `extractionModel` | ✅ Yes (unless using Ollama) |
| `autoRecall: true` | Reads from local SQLite | ❌ Never |
| Secret facts (`credentials`, `medical`, `financial`) | Filtered **before** extraction context | ❌ Never sent to LLM |

- **Secret facts** (`credentials`, `medical`, `financial`) are never sent to external APIs — they are filtered from the extraction dedup context before LLM calls
- **Private facts** stay within the agent that created them — they are never shared across agents
- **Shared facts** can appear in cross-agent recall (with provenance tags)
- All stored data lives locally in `~/.engram/conversations.sqlite` (or your configured `dataDir`)
- No cloud sync, telemetry, or external storage

**For fully local / air-gapped operation:** set `extractionModel` to `ollama/<model>` (e.g. `ollama/llama3`) and keep Ollama running on localhost. No API keys needed.

---

## Semantic Search (Embeddings)

Memento supports optional local semantic search via BGE-M3 (or any compatible GGUF embedding model):

```bash
# Download the BGE-M3 model (~1.3GB, Q8 quantization)
mkdir -p ~/.node-llama-cpp/models
curl -L -o ~/.node-llama-cpp/models/bge-m3-Q8_0.gguf \
  "https://huggingface.co/gpustack/bge-m3-GGUF/resolve/main/bge-m3-Q8_0.gguf"
```

The embedding engine uses GPU (CUDA) when available, falling back to CPU automatically. If no model is found, keyword (FTS5) search still works.

---

## License

MIT
