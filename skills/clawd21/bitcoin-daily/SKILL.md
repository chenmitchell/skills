---
name: bitcoin-daily
description: Daily digest of the Bitcoin Development mailing list and Bitcoin Core commits. Use when asked about recent bitcoin-dev discussions, mailing list activity, Bitcoin Core code changes, or to set up daily summaries. Fetches threads from groups.google.com/g/bitcoindev and commits from github.com/bitcoin/bitcoin.
metadata: {"clawdbot":{"emoji":"📰"}}
---

# Bitcoin Dev Digest (📰)

Daily summary of bitcoindev mailing list + Bitcoin Core commits.

## Commands

Run via: `node ~/workspace/skills/bitcoindev-digest/scripts/digest.js <command>`

| Command | Description |
|---------|-------------|
| `digest [YYYY-MM-DD]` | Fetch & summarize (default: yesterday) |
| `archive` | List all archived digests |
| `read <YYYY-MM-DD>` | Read a past summary |

## Output

The digest includes:
1. **Mailing list threads** — titles, links, and content previews from bitcoindev Google Group
2. **Bitcoin Core commits** — all merges to master since the target date

## Archive

Raw data archived to `~/workspace/bitcoin-dev-archive/YYYY-MM-DD/`:
- `mailing-list/*.json` — full thread content per topic
- `mailing-list/_index.json` — thread index
- `commits.json` — raw commit data
- `summary.md` — generated summary

## Daily Cron

Set up via Clawdbot cron to run every morning. The digest script fetches, archives, and outputs a summary that the agent then sends to the user.

## Sources

- Mailing list: https://groups.google.com/g/bitcoindev
- Bitcoin Core: https://github.com/bitcoin/bitcoin/commits/master/
