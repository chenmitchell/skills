# Email Inbound Cron

Run every 15 minutes to check for new emails.

## Steps

1. Run: `python3 skills/email-resend/scripts/inbound.py`

2. Parse the JSON output from inbound.py

3. Use `memory_search` tool to find channel preference:
   - Query: "email notification channel preference"
   
4. If found, deliver via `message` tool to the preferred channel
   
5. If not found in memory, use current context channel and ask user for preference

The script outputs JSON notification data - the agent handles delivery to the user's preferred channel via message tool.
