# OpenClaw Model Manager Skill 🛠️

Interact with OpenRouter API to fetch available models (with pricing and context window), and configure OpenClaw to use them via the `openrouter/auto` gateway or direct fallback configuration.

This skill solves the pain of manually editing `openclaw.json` or guessing model IDs. It fetches the **latest model list** from OpenRouter's public API, ranks them by popularity/power, displays pricing, and auto-generates the correct config patch.

## Features ✨

- **Zero-Config**: No API key required to browse models.
- **Real-Time Data**: Always fetches the latest models from OpenRouter.
- **Interactive**: List models in a clean table with context length & pricing.
- **Safe**: Generates a precise JSON patch for OpenClaw gateway configuration.
- **Smart**: Prioritizes popular models (GPT-4o, Claude 3.5 Sonnet, Llama 3) and filters out beta/test noise.

## Installation 📦

1. Clone this repository into your OpenClaw skills directory:
   ```bash
   cd ~/.openclaw/workspace/skills
   git clone https://github.com/YourUsername/openclaw-model-manager.git model-manager
   ```

2. That's it! OpenClaw will detect the `SKILL.md`.

## Usage 🚀

In your OpenClaw chat:

**List Models:**
> "list models"
> "列出模型"

**Enable a Model:**
> "enable 1"
> "启用 1" (where 1 is the index from the list)

**Manual Command:**
You can also run it from the terminal:
```bash
python3 skills/model-manager/manage_models.py list
python3 skills/model-manager/manage_models.py enable 1
```

## How it Works 🧠

1. **Fetches** `https://openrouter.ai/api/v1/models` (public API).
2. **Filters** for top-tier models and sorts by context length.
3. **Displays** a markdown table with pricing (input/output per 1M tokens).
4. **Patches** `~/.openclaw/openclaw.json` to add the selected model ID to `agents.defaults.models` and `fallbacks`.

## Requirements

- Python 3.6+ (uses standard library only, no pip install needed!)
- OpenClaw Gateway (local installation)

## License

MIT
