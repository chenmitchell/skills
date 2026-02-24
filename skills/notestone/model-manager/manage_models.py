import argparse
import json
import urllib.request
import urllib.error
import sys
import os

OPENROUTER_API = "https://openrouter.ai/api/v1/models"
CONFIG_FILE = os.path.expanduser("~/.openclaw/openclaw.json")

def fetch_models():
    """Fetch models from OpenRouter public API using standard library."""
    try:
        with urllib.request.urlopen(OPENROUTER_API, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('data', [])
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def filter_and_rank(models, limit=20):
    """Filter for popular/powerful models and rank them."""
    # Priority keywords for ranking
    priority_keywords = ["gpt-4o", "claude-3.5-sonnet", "o1-preview", "gemini-pro-1.5", "llama-3-70b", "deepseek-coder", "mistral-large", "qwen-2.5-72b"]
    
    ranked = []
    others = []
    
    for m in models:
        # Simple heuristic: prioritize models with specific keywords
        is_priority = any(k in m['id'] for k in priority_keywords)
        # Filter out very obscure or test models if needed
        if "test" in m['id'] or "beta" in m['id']: 
            if not is_priority: continue # Allow priority betas (e.g. o1-preview)
            
        if is_priority:
            ranked.append(m)
        else:
            others.append(m)
            
    # Sort priority models to top, then others by context length (descending)
    ranked.sort(key=lambda x: x['context_length'], reverse=True)
    others.sort(key=lambda x: x['context_length'], reverse=True)
    
    return (ranked + others)[:limit]

def display_models(models):
    """Print a markdown table of models."""
    print("| Index | ID | Context | Input Price ($/1M) | Output Price ($/1M) |")
    print("| :--- | :--- | :--- | :--- | :--- |")
    
    for idx, m in enumerate(models, 1):
        # Pricing is per token string, convert to float per 1M
        try:
            in_price = float(m['pricing']['prompt']) * 1_000_000
            out_price = float(m['pricing']['completion']) * 1_000_000
        except (ValueError, KeyError):
            in_price = 0.0
            out_price = 0.0
        
        name = m['id']
        # Highlight provider for readability
        if "/" in name:
            provider, model = name.split("/", 1)
            # name = f"**{provider}**/{model}" # Markdown bold
            
        print(f"| {idx} | `{m['id']}` | {m['context_length']//1000}k | ${in_price:.2f} | ${out_price:.2f} |")
        
    print("\nTo enable a model, use: `python3 skills/model-manager/manage_models.py enable <Index>`")

def enable_model(model_id, config_path):
    """Generate OpenClaw config patch to enable a model."""
    # Read current config to avoid overwriting existing
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return

    # Prepare patch data
    # We construct a JSON patch that merges deeply
    
    or_id = f"openrouter/{model_id}" if not model_id.startswith("openrouter/") else model_id
    
    # Get current fallbacks safely
    try:
        current_fallbacks = config['agents']['defaults']['model']['fallbacks']
    except KeyError:
        current_fallbacks = []
    
    new_fallbacks = list(current_fallbacks)
    if or_id not in new_fallbacks: new_fallbacks.append(or_id)
    
    # Construct the minimal patch object
    patch = {
        "agents": {
            "defaults": {
                "models": {
                    or_id: {}
                },
                "model": {
                    "fallbacks": new_fallbacks
                }
            }
        }
    }
    
    # Print the JSON for the agent to use with `config.patch` tool
    print(json.dumps(patch))

def main():
    if len(sys.argv) < 2:
        print("Usage: manage_models.py <list|enable> [target]")
        return

    action = sys.argv[1]
    
    models = fetch_models()
    if not models:
        return

    # Filter/Sort first to ensure indices match
    sorted_models = filter_and_rank(models)

    if action == "list":
        display_models(sorted_models)
        
    elif action == "enable":
        if len(sys.argv) < 3:
            print("Error: Please specify a model index to enable.")
            return
            
        target = sys.argv[2]
        selected_model_id = None
        
        # Check if target is an index (1-based)
        if target.isdigit():
            idx = int(target) - 1
            if 0 <= idx < len(sorted_models):
                selected_model_id = sorted_models[idx]['id']
        else:
            # Try to match string ID exactly
            for m in models:
                if m['id'] == target:
                    selected_model_id = m['id']
                    break
        
        if selected_model_id:
            enable_model(selected_model_id, CONFIG_FILE)
        else:
            print(f"Error: Model '{target}' not found.")

if __name__ == "__main__":
    main()
