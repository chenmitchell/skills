---
requires.env: RESEND_API_KEY
license: Apache-2.0
name: email-resend
description: >
  Send and receive emails using the Resend API. Use for: (1) sending emails directly
  via Resend API, (2) receiving email notifications via cron, (3) drafting replies with
  proper threading, (4) downloading attachments from inbound emails. Required env vars: RESEND_API_KEY.
  Auto-discovers user info from OpenClaw context or asks interactively.
---

# Email via Resend

Send and receive emails using the Resend API.

## Configuration

**No config file needed.** The skill auto-discovers settings from:

1. **OpenClaw context** — channel, chat_id, user email/name (from context)
2. **Environment variables** — for API keys
3. **Interactive prompts** — asks user if required info missing

### Required Environment Variables

```bash
export RESEND_API_KEY="re_123456789"        # Resend API key
# Channel/target set by agent from context/memory - not hardcoded
```

### First-Time Setup

When the skill is first invoked, the sub-agent should:

1. **Check context** — OpenClaw context already has:
   - `context.user.email` (from USER.md)
   - `context.channel` (from current session)
   - `context.chat_id`
   - `context.thread_id` (for topics)

2. **Check memory** — Use `memory_search` tool:
   - Query: "email notification channel preference"
   - Query: "email from address"

3. **If missing, ask user** — Via chat message:
   - "Which email should I send from?"
   - "Which channel for email notifications?"

4. **Commit to memory** — Write preferences to persist across sessions:
   ```bash
   write path="memory/email-preferences.md" content="---
   from_email: $EMAIL
   from_name: $NAME
   notification_channel: $CHANNEL
   chat_id: \"$CHAT_ID\"
   thread_id: \"$THREAD_ID\"
   ---
   
   # Email Notification Preferences
   Saved $(date)
   "
   ```
   This ensures memory_search finds it in future sessions.

**Format (YAML frontmatter):**
```markdown
---
from_email: you@company.com
from_name: Your Name
notification_channel: telegram  # or discord, signal, whatsapp, etc - from memory or ask user
chat_id: "123456789"
thread_id: "334"  # optional, for topics
---
```

### Context Fields (Available in Sub-Agent)

| Field | Source | Example |
|-------|--------|---------|
| `user.email` | USER.md | `you@company.com` |
| `user.name` | USER.md | `Your Name` |
| `channel` | OpenClaw | from context |
| `chat_id` | OpenClaw | `123456789` |
| `thread_id` | OpenClaw | `334` |

The skill uses these directly from OpenClaw context — no parsing needed.

## Usage

## Inbound (Receive)

### Cron Setup

```bash
openclaw cron add \
  --name "email-resend-inbound" \
  --every 15m \
  --session-target isolated \
  --message "Follow instructions in skills/email-resend/cron-prompts/email-inbound.md" \
  --to "YOUR_CHAT_ID" \
  --announce
```

### Manual Check

```bash
python3 skills/email-resend/scripts/inbound.py
```

### Notification Format

Each new email triggers a notification with:
- From, Subject, Date
- Body preview (~2000 chars)
- Attachment list (if any)
- Importance: 🔥 HIGH / 📅 MEETING / 📬 NORMAL

### Acknowledge Flow

Reply to the notification message (using notification reply) to acknowledge, or type:
- `done` / `ack` - mark as read

Use `draft-reply.py` to compose replies with proper quoting.

**Important:** Always use inline replies (`[[reply_to_current]]`) to keep messages linked in the thread. This enables:
- Proper custody chain tracking
- Reply-to-email tracing
- Better conversation flow

**CRITICAL:** When responding via OpenClaw message tool, use `replyTo` parameter (not `[[reply_to_current]]` tag):
```python
message(action="send", channel="<from-context>", replyTo="<msg_id>", ...)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `inbound.py` | Check emails, send notifications |
| `draft-reply.py` | Draft reply workflow with quoting & threading |
| `outbound.py` | Send emails directly |
| `download_attachment.py` | Download attachments from inbound emails |

### Downloading Attachments

To download attachments from an inbound email:

```bash
# List attachments (shows IDs)
python3 scripts/download_attachment.py <email_id> --list

# Download all to directory
python3 scripts/download_attachment.py <email_id> --output-dir ./attachments

# Download specific attachment
python3 scripts/download_attachment.py <email_id> --attachment-id <attachment_id>
```

**Note:** The API path is `/emails/receiving/{email_id}/attachments` (not the standard `/emails/` path).

## State Files

- `memory/email-resend-inbound-notified.json` — pending/acknowledged emails
- `memory/email-message-map.json` — notification message_id → email_id (legacy)
- `memory/email-custody-chain.json` — Full DAG of email → notification → actions
- `memory/email-msg-to-chain.json` — notification message_id → chain lookup
- `memory/email-draft-state.json` — Active draft state (email_id, status, reply_content)

See `docs/custody-chain.md` for DAG design.

## Outbound (Send)

```bash
python3 skills/email-resend/scripts/outbound.py \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "Message text"

# With attachments
python3 skills/email-resend/scripts/outbound.py \
  --to "recipient@example.com" \
  --subject "Here's the file" \
  --body "See attachment" \
  --attachment ./file.pdf \
  --attachment ./image.png
```

## ⚠️ CRITICAL: Email Threading Rule (2026-02-22)

**MANDATORY: Always use `draft-reply.py` for replying to emails.**

This is non-negotiable. Failure to follow this rule will result in broken Gmail threading.

### Why This Matters
- Gmail threads emails based on `In-Reply-To` AND `References` headers
- Using wrong headers = reply appears as NEW thread = context lost
- There's no way to fix this after sending

### ✅ Correct Workflow (ALWAYS USE THIS)

```bash
# Step 1: Start draft (fetches Message-ID automatically)
python3 skills/email-resend/scripts/draft-reply.py start <email_id>

# Step 2: Set reply content
python3 skills/email-resend/scripts/draft-reply.py content "Your reply"

# Step 3: Send
python3 skills/email-resend/scripts/draft-reply.py send
```

### ⚠️ CRITICAL: Approval Execution Rule (2026-02-22)

**When user approves a draft, you MUST execute the send command immediately.**

**The mistake to avoid:**
- ❌ Show draft for approval → User says "send" → Only acknowledge, don't execute
- ✅ Show draft for approval → User says "send" → RUN `draft-reply.py send` → Then confirm

**Correct workflow:**
```
1. Show draft for approval
2. User replies "approve", "send", "yes", or "ok"
3. IMMEDIATELY run: draft-reply.py send
4. Only THEN confirm to user
```

**Never:**
- Only acknowledge the approval without executing
- Ask for confirmation after user already approved
- Wait to send - do it immediately

### ❌ NEVER Do These Things

**NEVER use `outbound.py` for replies:**
```bash
# WRONG - will break threading
python3 skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Original" --body "Reply"
```

**NEVER manually construct `--reply-to` flags:**
```bash
# WRONG - guessing Message-ID format never works
python3 skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Original" --body "Reply" \
  --reply-to "<some-guess>@resend"
```

**NEVER skip the workflow when subject starts with "Re:":**
```bash
# WRONG - replying without threading headers breaks thread
python3 skills/email-resend/scripts/outbound.py \
  --to "x@y.com" --subject "Re: Previous Thread" --body "Quick reply"
```

### outbound.py Only For New Emails

`outbound.py` is for **new emails only** (not replies):
- First contact
- Announcements
- Emails where you intentionally want a NEW thread

For anything that could be a reply, use `draft-reply.py`.

## Requirements

- `RESEND_API_KEY` environment variable set
- Python `requests` library

## Draft Reply Best Practices

When composing a reply via `draft-reply.py`:

1. **Always quote the original** — Include the original message with `>` prefix so recipient knows what you're responding to

2. **Use proper threading** — Set `In-Reply-To` and `References` headers using the original email's Message-ID

3. **Keep subject line** — Start with `Re: ` prefix to maintain thread (but avoid "Re: Re:")

4. **Structure:**
   ```
   Your reply here

   ---

   On [date] [original sender] wrote:
   > quoted original message
   > continues here
   ```

5. **Multiple replies supported** — After sending, draft is marked as "sent" so you can reply again to the same thread. Use `resume` command to continue.

6. **No double Re:** — If original subject already starts with "Re:", don't add another

7. **Custody Chain** — Track full lineage:
   - Email → notification → All replies/actions
   - DAG structure with parent links
   - Any message traces back to original email

## Draft Reply Commands

| Command | Purpose |
|---------|---------|
| `start <email_id>` | Start a draft reply to an email |
| `resume` | Continue a sent thread to reply again |
| `content "text"` | Set reply content |
| `send` | Send the reply |
| `cancel` | Cancel the draft |
| `status` | Show current draft status |

After sending, use `resume` to reply again to the same thread — threading headers are preserved.

Run tests:
```bash
python3 skills/email-resend/tests/test_inbound.py
```

Expected: 40 tests, all passing.

If tests fail:
1. Check which test failed and why
2. Fix the feature/code to match expected behavior
3. Or update tests if feature intentionally changed
