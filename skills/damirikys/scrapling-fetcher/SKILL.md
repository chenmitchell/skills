---
name: scrapling
description: Web scraping using Scrapling — a Python framework with anti-bot bypass (Cloudflare Turnstile, fingerprint spoofing), adaptive element tracking, stealth headless browser, and full CSS/XPath extraction. Use when web_fetch fails (Cloudflare, JS-rendered pages, paywalls), when extracting structured data from websites (prices, articles, lists), or when building scrapers that survive site redesigns. Supports HTTP, stealth, and full browser modes.
---

# Scrapling Skill

Scrapling is installed at system level (`pip install scrapling[all]`). Chromium is available for headless browser modes.

## Script

`scripts/scrape.py` — CLI wrapper for all three fetcher modes.

```bash
# Basic fetch (text output)
python3 ~/skills/scrapling/scripts/scrape.py <url>

# CSS selector
python3 ~/skills/scrapling/scripts/scrape.py <url> --selector ".class" 

# Stealth mode (Cloudflare bypass)
python3 ~/skills/scrapling/scripts/scrape.py <url> --mode stealth

# JSON output
python3 ~/skills/scrapling/scripts/scrape.py <url> --selector "h2" --json

# Quiet (suppress INFO logs)
python3 ~/skills/scrapling/scripts/scrape.py <url> -q
```

## Fetcher Modes

- **http** (default) — Fast HTTP with browser TLS fingerprint spoofing. Most sites.
- **stealth** — Headless Chrome with anti-detect. For Cloudflare/anti-bot.
- **dynamic** — Full Playwright browser. For heavy JS SPAs.

## When to Use Each Mode

- `web_fetch` returns 403/429/Cloudflare challenge → use `--mode stealth`
- Page content requires JS execution → use `--mode dynamic`
- Regular site, just need text/data → use `--mode http` (default)

## Python Inline Usage

For custom logic beyond what the CLI covers, write inline Python. See `references/patterns.md` for:
- Adaptive scraping (survives redesigns)
- Session/cookie handling
- Async usage
- XPath, find_similar, attribute extraction
- MCP server setup

## Notes

- Stealth/dynamic modes require display; they use Chromium headless (no `xvfb-run` needed).
- `auto_save=True` on first scrape saves element fingerprints for future adaptive runs.
- For large-scale crawls, use the Spider API (see Scrapling docs).
