---
name: leetify
description: Get CS2/CS:GO player statistics, match analysis, and gameplay insights from Leetify API. Uses Telegram username to Steam ID mapping for easy access. Use when asked for "анализ демки", "разбор демки", "разбор матча", "что я сделал не так", "demo analysis".
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "env": ["LEETIFY_API_KEY"],
            "bins": ["python3", "bash", "bunzip2", "gunzip"],
            "pip": ["requests", "demoparser2"],
          },
      },
  }
---

# Leetify API Skill

Get CS2/CS:GO statistics from Leetify platform.

## start Quick Stats (Default)

Avoid downloading or analyzing a demo unless explicitly requested (e.g. "demo analysis", "разбор демки"). For general stat queries, use the commands below to save time and resources.

### Show Statistics
```bash
bash scripts/get_stats_by_username.sh USERNAME
```
*Shows: Averages (100 games), last 5 matches (K/D/A, ADR, HS, MVPs), ranks, general stats.*

### Get Match Data (JSON for Analysis)
```bash
bash scripts/get_match_details.sh USERNAME [INDEX]
```
*Outputs: Full raw JSON statistics for a specific match.* 
**Model Instruction:** When presenting this data, ALWAYS format the JSON into a readable report with emojis. Separate logical blocks (e.g., stats General, shooting Shooting, recommendations Utility, mistakes Mistakes).

### Compare Players
```bash
bash scripts/compare_by_username.sh USERNAME1 USERNAME2
```

### Clan Season Stats
```bash
python3 scripts/season_stats.py
```
*Shows: Summary table for all clan members for the current season.*

## demo Demo Analysis (for "разбор демки", "анализ демки", "demo analysis")

**When the user asks for demo analysis, match breakdown, or tactical review — ALWAYS use this workflow:**

### Step 1: Identify the Player and current In-Game Name (IGN)
- Get Steam ID: `python3 scripts/steam_ids.py get --username USERNAME`
- The scoreboard includes Steam IDs in `[steamid]` format next to each player name. Always match the target player by their Steam ID to ensure accuracy.
- Workflow: get Steam ID -> find the line in SCOREBOARD with that exact Steam ID -> that's your player.

### Step 2: Generate the match log
```bash
python3 scripts/analyze_last_demo.py --username USERNAME [--match-index N] [--no-cache]
```
- Downloads the demo (50-300MB), parses it with demoparser2
- Outputs a compact text log: scoreboard + round-by-round timeline
- Caches result in `matches/{match_id}.txt` (use `--no-cache` to re-parse)

### Step 3: Analyze the log

Read the full output and produce a structured analysis for the requested player.
**Use emojis and beautiful formatting throughout the analysis.**

**Analysis Guidelines (Structure, Tone & Positions):**
- **Structure:** 
  1. **stats General Stats** — K/D/A, ADR, HS%, KAST%, multikills, clutches.
  2. **role Role Assessment** — Identify role (Entry, Anchor, Support, Lurker, Sniper, Rifler, Rotator) and evaluate effectiveness.
  3. **side T-Side** — Utility usage, positioning, key mistakes, entry success/failure.
  4. **side CT-Side** — Site anchor position, rotations, utility usage.
  5. **mistakes Mistakes & Failures** — Specific moments of poor play, baiting teammates, or giving away free kills (with timestamps).
  6. **highlights Highlights** — Key plays, clutches, multikills (with timestamps).
  7. **positioning Positioning** — Analyze frequently played positions. **MANDATORY if the player failed their role/position:** Search the web for guides/videos (YouTube/Steam Guides/CS2 sites) for these specific positions on the current map and include links. If they played perfectly, guides are optional.
  8. **recommendations Recommendations** — Concrete, actionable advice.
  9. **rating Overall Rating** — X/10 score.
- **Tone & Objectivity:** Be neutral and objective. Do not sugarcoat bad performance. Context is key: do not praise high stats (e.g. HS%) if they had no impact on the round win. Call out bad play explicitly (baiting, hunting for eco frags, playing for stats).
- **Position Naming:** Translate raw positions. Do not use internal names (e.g. "SideAlley", "BombsiteA"). Use common community callouts: Mid, Connector, Jungle, Short, Long, Tunnel, etc.

**What to look for in the log:**
- `KILL` lines: who killed whom, with what weapon, HS/wallbang/smoke/blind tags, <-opening/<-trade annotations
- `DMG` lines: damage exchanges, health tracking
- `FLASH` lines: team flashes (marked `TEAM!`), effective enemy flashes (duration)
- `POS` lines: player positions every ~5s — where the player is relative to teammates and action
- `NADE` lines: utility usage and timing
- Economy block: buy type, equipment value, item purchases
- `RESULT` line: round winner, clutch attempts with ok/fail
- `HALVES` line: half scores for macro analysis

### Options
```bash
# Specific round deep-dive
python3 scripts/analyze_last_demo.py --username USERNAME --round N

# Older match (0=last, 1=previous, etc.)
python3 scripts/analyze_last_demo.py --username USERNAME --match-index 1

# Force re-parse (skip cache)
python3 scripts/analyze_last_demo.py --username USERNAME --no-cache
```

### warning Memory constraints
- Server has 2GB RAM — the parser is optimized but large demos may be tight
- Economy is parsed in chunks of 4 rounds, positions per-round with gc.collect()
- If OOM occurs, try running without other heavy processes

## tools Management

### Manage Steam IDs
```bash
# Save
python3 scripts/steam_ids.py save --username "jeminay" --steam-id "76561198185608989" --name "Дамир"

# Get
python3 scripts/steam_ids.py get --username "jeminay"

# List all
python3 scripts/steam_ids.py list
```

## recommendations Analysis Workflow

1. **Check Steam ID:** `python3 scripts/steam_ids.py get --username USERNAME`
2. **Run demo parser:** `python3 scripts/analyze_last_demo.py --username USERNAME`
3. **Read the full log** — identify the target player's team, side, position patterns
4. **Match teammates:** Cross-reference with `scripts/steam_ids.py list` to identify known players
5. **Analyze round-by-round:** Track the player's kills, deaths, utility, positions, economy
6. **Write structured analysis** in Russian (unless specified otherwise). Apply Analysis Guidelines strictly.

**Key rules:**
- Show script output AS IS when asked for raw data.
- For analysis: read the log thoroughly and write a precise breakdown.
- Always mention specific rounds and timestamps (e.g., "R5 [45s]").
- **Web Search Condition:** If the player failed their role or specific positions, use `web_search` to find tutorials or position guides for these primary positions and attach them to the Positioning section.
- Highlight patterns, trends, and tactical errors, not just isolated events.

## Configuration

Set the `LEETIFY_API_KEY` environment variable with your Leetify API key.
You can get it from: https://api-public-docs.cs-prod.leetify.com/

## API Docs

Docs: https://api-public-docs.cs-prod.leetify.com/
