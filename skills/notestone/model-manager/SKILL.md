# Model Manager Skill

Interact with OpenRouter API to fetch available models (with pricing and context window), and configure OpenClaw to use them via the `openrouter/auto` gateway or direct fallback configuration.

## Commands

- `list models` or `ls models` or `列出模型`: Fetch and display top models from OpenRouter.
- `enable <model_id>` or `启用 <model_id>`: Add a model to OpenClaw's configuration (agents.defaults.models & fallbacks).

## Implementation Details

This skill uses a Python script `manage_models.py` to:
1. Fetch `https://openrouter.ai/api/v1/models` (public API, no key needed).
2. Filter and rank models (e.g., sort by context length, pricing, or popularity).
3. Generate `config.patch` commands for OpenClaw.

## Usage Example

User: "list models"
Agent: (Runs script, displays table)
| ID | Name | Context | Price |
| :--- | :--- | :--- | :--- |
| 1 | `anthropic/claude-3.5-sonnet` | 200k | $3/$15 |
...

User: "enable 1"
Agent: (Runs config patch) "Model enabled! You can now use it in tasks."
