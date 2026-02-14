---
name: link-brain
description: "Save and search links, articles, videos, and anything from the web. Acts as a personal knowledge base -- send any URL and it gets read, summarized, tagged, and stored for instant recall later. Use when a user shares a link to save, asks to find a previously saved link, wants to search their saved content, or says things like 'save this', 'remember this link', 'bookmark this', 'what was that article about X'. Also use when listing saved links, browsing by tag, or exporting the collection."
---

# Link Brain

Personal knowledge base for links. Save anything, find it later by describing what you remember.

## How it works

1. User shares a URL (or says "save this")
2. You fetch the content with `web_fetch`, read it, write a short summary
3. You store it with `brain.py save` including title, summary, and tags
4. Later, user asks "what was that article about X" and you search with `brain.py search`

## Setup

No API keys. Needs `python3`. Data lives in `~/.link-brain/brain.db` (SQLite).

## Saving a link

When a user shares a URL to save:

1. Fetch the page: use the `web_fetch` tool to get the content
2. Read it and write a 2-3 sentence summary (in your own words, not copy-paste)
3. Pick 3-5 relevant tags
4. Detect the type (article, video, podcast, pdf, repo, social)
5. Save it:

```bash
python3 scripts/brain.py save "https://example.com/article" \
  --title "How batteries actually work" \
  --summary "Breaks down lithium-ion chemistry in plain language. Covers why batteries degrade over time and what solid-state batteries might change. Good primer for non-engineers." \
  --tags "batteries, energy, science, explainer"
```

Keep summaries useful. Write what someone would need to remember *why* they saved it.

## Searching

```bash
python3 scripts/brain.py search "batteries"
python3 scripts/brain.py search "that article about sleep"
python3 scripts/brain.py search "react performance" --limit 5
```

Full-text search across titles, summaries, tags, and URLs. Falls back to fuzzy matching if exact search returns nothing.

## Other commands

```bash
python3 scripts/brain.py recent              # Last 20 saved links
python3 scripts/brain.py recent --limit 5    # Last 5
python3 scripts/brain.py tags                # All tags with counts
python3 scripts/brain.py tags "python"       # Links tagged "python"
python3 scripts/brain.py get 42              # Full details for link #42
python3 scripts/brain.py delete 42           # Remove a link
python3 scripts/brain.py stats               # Collection overview
python3 scripts/brain.py export              # Dump everything as JSON
```

## When users ask to find something

They'll say vague stuff like:
- "What was that article about solar panels?"
- "Find the link about Rust performance I saved last month"
- "Show me everything tagged finance"

Run a search, show the top results with title + summary + URL. If multiple matches, list them briefly and let the user pick.

## Tips

- Auto-detect when someone drops a URL in chat without explicitly saying "save" -- ask if they want to save it
- When saving, always fetch and read the content first so the summary is actually useful
- Tags should be lowercase, broad enough to be reusable (prefer "python" over "python-3.12-asyncio-bug")
- The summary is the most important part -- it's what makes search work well later
