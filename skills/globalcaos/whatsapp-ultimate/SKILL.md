---
name: whatsapp-ultimate
version: 1.9.0
description: "Complete WhatsApp integration for OpenClaw agents — send messages, media, polls, stickers, voice notes, reactions & replies. Search chat history with full-text search (SQLite + FTS5). Download & transcribe voice messages. Import chat exports. Full history resync. NEW: 🤔↔🧐 Thinking Heartbeat — alternating reaction indicator (~1s) that doubles as a watchdog (frozen = hung). Owner voice messages bypass prefix filters. Native Baileys — zero Docker, zero external tools. Works alongside OpenClaw's built-in WhatsApp channel."
homepage: https://github.com/globalcaos/clawdbot-moltbot-openclaw
repository: https://github.com/globalcaos/clawdbot-moltbot-openclaw
metadata:
  openclaw:
    emoji: "📱"
    requires:
      channels: ["whatsapp"]
    tags:
      - whatsapp
      - messaging
      - chat
      - voice-notes
      - group-management
      - message-history
      - search
      - media
      - polls
      - stickers
      - reactions
      - thinking-indicator
      - progress-indicator
      - typing-indicator
      - voice-messages
      - baileys
---

# WhatsApp Ultimate

**Send messages, media, polls, voice notes, and manage groups — all from your AI agent. Search your entire WhatsApp history instantly.**

The most complete WhatsApp skill for OpenClaw. Native Baileys integration — no Docker, no CLI tools, no external services. Just connect and go.

---

## Prerequisites

- OpenClaw with WhatsApp channel configured
- WhatsApp account linked via QR code (`openclaw whatsapp login`)

---

## Capabilities Overview

| Category         | Features                                                                    |
| ---------------- | --------------------------------------------------------------------------- |
| **Messaging**    | Text, media, polls, stickers, voice notes, GIFs                             |
| **Interactions** | Reactions, replies/quotes, edit, unsend                                     |
| **Groups**       | Create, rename, icon, description, participants, admin, invite links        |
| **Progress**     | 🤔 Thinking reaction (visible processing indicator for groups)              |
| **Media Bypass** | Owner voice/media messages bypass prefix filters in groups                  |
| **History**      | Persistent SQLite storage, FTS5 full-text search, import historical exports |
| **Resync**       | Full history re-sync via re-link, automatic backup & restore                |

**Total: 24 distinct actions + searchable history**

---

## 🤔 Thinking Reaction (Progress Indicator)

**The problem:** WhatsApp linked devices (Baileys, Web API) cannot show "typing..." indicators in group chats. This is a WhatsApp server-side limitation — the protocol sends the `chatstate` XML node correctly, but WhatsApp's servers don't relay composing presence from companion devices to group participants. Confirmed in [Baileys #866](https://github.com/WhiskeySockets/Baileys/issues/866).

**The solution:** When your agent starts processing a message, it instantly reacts with 🤔 on the triggering message. When the reply is ready, the reaction is automatically removed. This gives users immediate visual feedback that the agent is working — no more wondering if your message was received.

**How it works:**
1. Message arrives → agent reacts with 🤔 (instant, <100ms)
2. Agent processes (tools, thinking, API calls...)
3. Reply delivered → 🤔 removed automatically

**Works in:** Groups ✅ | DMs ✅ | All chat types

This is the **only WhatsApp skill** that solves the invisible-typing-indicator problem. Every other WhatsApp integration leaves users staring at silence while the agent thinks.

---

## Owner Media Bypass

Voice messages and media from the bot owner now bypass the `triggerPrefix` filter in groups. Previously, a voice note sent in a group with `triggerPrefix: "Jarvis"` would be silently dropped because audio can't carry a text prefix. Now owner media messages are automatically routed to the agent.

---

## Messaging

### Send Text

```
message action=send channel=whatsapp to="+34612345678" message="Hello!"
```

### Send Media (Image/Video/Document)

```
message action=send channel=whatsapp to="+34612345678" message="Check this out" filePath=/path/to/image.jpg
```

Supported: JPG, PNG, GIF, MP4, PDF, DOC, etc.

### Send Poll

```
message action=poll channel=whatsapp to="+34612345678" pollQuestion="What time?" pollOption=["3pm", "4pm", "5pm"]
```

### Send Sticker

```
message action=sticker channel=whatsapp to="+34612345678" filePath=/path/to/sticker.webp
```

Must be WebP format, ideally 512x512.

### Send Voice Note

```
message action=send channel=whatsapp to="+34612345678" filePath=/path/to/audio.ogg asVoice=true
```

**Critical:** Use OGG/Opus format for WhatsApp voice notes. MP3 may not play correctly.

### Send GIF

```
message action=send channel=whatsapp to="+34612345678" filePath=/path/to/animation.mp4 gifPlayback=true
```

Convert GIF to MP4 first (WhatsApp requires this):

```bash
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4 -y
```

---

## Interactions

### Add Reaction

```
message action=react channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" emoji="🚀"
```

### Remove Reaction

```
message action=react channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" remove=true
```

### Reply/Quote Message

```
message action=reply channel=whatsapp to="34612345678@s.whatsapp.net" replyTo="QUOTED_MSG_ID" message="Replying to this!"
```

### Edit Message (Own Messages Only)

```
message action=edit channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" message="Updated text"
```

### Unsend/Delete Message

```
message action=unsend channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123"
```

---

## Group Management

### Create Group

```
message action=group-create channel=whatsapp name="Project Team" participants=["+34612345678", "+34687654321"]
```

### Rename Group

```
message action=renameGroup channel=whatsapp groupId="123456789@g.us" name="New Name"
```

### Set Group Icon

```
message action=setGroupIcon channel=whatsapp groupId="123456789@g.us" filePath=/path/to/icon.jpg
```

### Set Group Description

```
message action=setGroupDescription channel=whatsapp groupJid="123456789@g.us" description="Team chat for Q1 project"
```

### Add Participant

```
message action=addParticipant channel=whatsapp groupId="123456789@g.us" participant="+34612345678"
```

### Remove Participant

```
message action=removeParticipant channel=whatsapp groupId="123456789@g.us" participant="+34612345678"
```

### Promote to Admin

```
message action=promoteParticipant channel=whatsapp groupJid="123456789@g.us" participants=["+34612345678"]
```

### Demote from Admin

```
message action=demoteParticipant channel=whatsapp groupJid="123456789@g.us" participants=["+34612345678"]
```

### Leave Group

```
message action=leaveGroup channel=whatsapp groupId="123456789@g.us"
```

### Get Invite Link

```
message action=getInviteCode channel=whatsapp groupJid="123456789@g.us"
```

Returns: `https://chat.whatsapp.com/XXXXX`

### Revoke Invite Link

```
message action=revokeInviteCode channel=whatsapp groupJid="123456789@g.us"
```

### Get Group Info

```
message action=getGroupInfo channel=whatsapp groupJid="123456789@g.us"
```

Returns: name, description, participants, admins, creation date.

---

## Access Control

### DM Policy

Control who can DM your agent in `openclaw.json`:

```json
{
  "channels": {
    "whatsapp": {
      "dmPolicy": "allowlist",
      "allowFrom": ["+34612345678", "+14155551234"],
      "triggerPrefix": "Jarvis"
    }
  }
}
```

| Policy        | Behavior                                |
| ------------- | --------------------------------------- |
| `"open"`      | Anyone can DM                           |
| `"allowlist"` | Only numbers in `allowFrom` can DM      |
| `"pairing"`   | Unknown senders get pairing code prompt |
| `"disabled"`  | No DMs accepted                         |

### Group Policy

```json
{
  "channels": {
    "whatsapp": {
      "groupPolicy": "open",
      "groupAllowFrom": ["+34612345678", "+14155551234"]
    }
  }
}
```

| Policy        | Behavior                              |
| ------------- | ------------------------------------- |
| `"open"`      | Responds to mentions in any group     |
| `"allowlist"` | Only from senders in `groupAllowFrom` |
| `"disabled"`  | Ignores all group messages            |

### Self-Chat Mode

```json
{
  "channels": {
    "whatsapp": {
      "selfChatMode": true
    }
  }
}
```

Allows messaging yourself (your "Note to Self" chat) to interact with the agent.

### Trigger Prefix

```json
{
  "channels": {
    "whatsapp": {
      "triggerPrefix": "Jarvis"
    }
  }
}
```

Messages must start with this prefix to trigger the agent. Works in:

- Self-chat
- Allowed DMs
- Any DM where you (the owner) message with the prefix

### Message Prefix (Outbound Identity)

```json
{
  "channels": {
    "whatsapp": {
      "messagePrefix": "🤖"
    }
  }
}
```

All outbound messages from the agent are prefixed with this string. Use an emoji (like 🤖) so recipients can instantly tell who's talking — especially useful in group chats or when the agent sends from your personal number. Common choices:

- `🤖` — robot face (recommended)
- `[Jarvis]` — named tag
- Any short identifier that distinguishes agent messages from your own

---

## JID Formats

WhatsApp uses JIDs (Jabber IDs) internally:

| Type       | Format                    | Example                      |
| ---------- | ------------------------- | ---------------------------- |
| Individual | `<number>@s.whatsapp.net` | `34612345678@s.whatsapp.net` |
| Group      | `<id>@g.us`               | `123456789012345678@g.us`    |

When using `to=` with phone numbers, OpenClaw auto-converts to JID format.

---

## Tips

### Resolving Group Names

The history database often has `NULL` for `chat_name`. To get a group's display name, use:

```
message action=getGroupInfo channel=whatsapp target="<group-jid>"
```

Returns: `subject` (group name), `description`, full participant list with admin roles.

**Always refer to groups by name when talking to humans** — JIDs are internal identifiers only.

### Voice Notes

Always use OGG/Opus format:

```bash
ffmpeg -i input.wav -c:a libopus -b:a 64k output.ogg
```

### Stickers

Convert images to WebP stickers:

```bash
ffmpeg -i input.png -vf "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2:color=0x00000000" output.webp
```

### Clean DM Behavior (Recommended Config)

WhatsApp is a small-screen medium. Only send the **final response** — never tool events, intermediate status, or debug output. The typing indicator (three dots) is sufficient progress feedback.

**Set verbose off** in your OpenClaw config:

```json
{
  "agents": {
    "defaults": {
      "verboseDefault": "off"
    }
  }
}
```

This prevents `[openclaw] 🛠️ Exec: ...`, `[openclaw] 📖 Read`, etc. from flooding the chat as separate messages.

**Voice note replies should include the transcript** — when a user sends a voice message, include the transcribed text in your written reply so they can verify what was understood.

### Rate Limits

WhatsApp has anti-spam measures. Avoid:

- Bulk messaging to many contacts
- Rapid-fire messages
- Messages to contacts who haven't messaged you first

### Message IDs

To react/edit/unsend, you need the message ID. Incoming messages include this in the event payload. For your own sent messages, the send response includes the ID.

---

## When to Use This Skill

Use `whatsapp-ultimate` when your agent needs to:

- Send text, images, videos, documents, or voice notes via WhatsApp
- Create and manage polls in group chats
- React to messages with emoji, reply/quote, edit or unsend messages
- Create groups, manage participants, get invite links
- Search past WhatsApp conversations by keyword, sender, or date
- Import and index WhatsApp chat export files (.txt)
- Get group metadata (name, description, participant list)
- Set up automated daily summaries of busy group chats

## Comparison with Other Skills

| Feature                         | whatsapp-ultimate                                                         | wacli                       | whatsapp-business       |
| ------------------------------- | ------------------------------------------------------------------------- | --------------------------- | ----------------------- |
| Native integration              | ✅ Zero deps                                                              | ❌ Go CLI binary            | ❌ External API + key   |
| Send text                       | ✅                                                                        | ✅                          | ✅                      |
| Send media                      | ✅                                                                        | ✅ (files)                  | ✅ (templates)          |
| Polls                           | ✅                                                                        | ❌                          | ❌                      |
| Stickers                        | ✅                                                                        | ❌                          | ❌                      |
| Voice notes                     | ✅                                                                        | ❌                          | ❌                      |
| GIFs                            | ✅                                                                        | ❌                          | ❌                      |
| Reactions                       | ✅                                                                        | ❌                          | ❌                      |
| Reply/Quote                     | ✅                                                                        | ❌                          | ❌                      |
| Edit messages                   | ✅                                                                        | ❌                          | ❌                      |
| Unsend/Delete                   | ✅                                                                        | ❌                          | ❌                      |
| Group management                | ✅ (full: create, rename, icon, description, participants, admin, invite) | ❌                          | ❌                      |
| Group info/metadata             | ✅                                                                        | ❌                          | ❌                      |
| Two-way chat                    | ✅                                                                        | ❌                          | ✅ (webhooks)           |
| Message history (SQLite + FTS5) | ✅                                                                        | ✅ (sync)                   | ❌                      |
| Import chat exports             | ✅                                                                        | ❌                          | ❌                      |
| Personal WhatsApp               | ✅                                                                        | ✅                          | ❌ (Business only)      |
| External deps                   | **None**                                                                  | Go binary (brew/go install) | Maton API key + account |
| **Total actions**               | **22+**                                                                   | ~6                          | ~10                     |

---

## Message History & Search (v1.2.0+)

OpenClaw now stores **all WhatsApp messages** in a local SQLite database with full-text search (FTS5). Never lose a conversation again.

### How It Works

```
Live Messages (Baileys) ──┐
                          ├──→ SQLite + FTS5 ──→ whatsapp_history tool
WhatsApp Exports (.txt) ──┘
```

- **Live capture:** Every new message automatically saved
- **Historical import:** Bulk import from WhatsApp chat exports
- **Full-text search:** Find any message by content, sender, or chat

### Searching History

Use the `whatsapp_history` tool (available to your agent automatically):

```
# Search by keyword
whatsapp_history action=search query="meeting tomorrow"

# Filter by chat
whatsapp_history action=search chat="Family Group" limit=50

# Find what you said
whatsapp_history action=search fromMe=true query="I promised"

# Filter by sender
whatsapp_history action=search sender="John" limit=20

# Date range
whatsapp_history action=search since="2026-01-01" until="2026-02-01"

# Database stats
whatsapp_history action=stats
```

### Importing Historical Messages

WhatsApp doesn't expose infinite history via API. To get older messages:

1. **Export from phone:** Settings → Chats → Chat history → Export chat → Without media
2. **Save the .txt files** somewhere accessible
3. **Import:**

```
whatsapp_history action=import path="/path/to/exports"
```

Or import a single chat:

```
whatsapp_history action=import path="/path/to/chat.txt" chatName="Family Group"
```

### Database Location

```
~/.openclaw/data/whatsapp-history.db
```

SQLite file with WAL mode for concurrent access.

### Use Cases

- _"What did I tell Sarah about the meeting?"_
- _"Find all messages mentioning 'deadline'"_
- _"Show my recent messages to the work group"_
- _"When did John mention the quarterly report?"_

The agent can now answer these questions by searching your complete WhatsApp history.

### Automated Daily Summaries (Cron Pattern)

Set up a daily cron job to summarize busy group chats:

```json
{
  "name": "whatsapp-group-summary",
  "schedule": { "kind": "cron", "expr": "30 5 * * *", "tz": "America/Los_Angeles" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Search yesterday's WhatsApp messages using whatsapp_history. For groups with 20+ messages, generate a summary with key topics and action items. Send via message tool to the target group."
  }
}
```

Your agent wakes up, reads yesterday's chats, and delivers a morning briefing. No manual effort.

---

## Download & Transcribe Voice Messages (v1.3.0+)

The history database stores the **full raw WAMessage proto** (including media keys) in the `raw_json` column. This means you can download and decrypt any voice message, image, video, or document — even from group chats, even from other people.

### How It Works

```
SQLite raw_json ──→ Extract audioMessage/imageMessage ──→ Baileys downloadContentFromMessage() ──→ File
```

WhatsApp encrypts media with a per-message key. The key is stored in the proto — Baileys handles decryption transparently.

### Download a Voice Message

1. **Find the message ID** via `whatsapp_history`:

```
whatsapp_history action=search chat="GROUP_JID" sender="PersonName" limit=10
```

Look for messages with `type: "voice"` or `type: "audio"`.

2. **Download the audio** using a Node.js script (must run from the OpenClaw source dir for Baileys access):

```bash
cd /path/to/openclaw/source && node -e "
const { downloadContentFromMessage } = require('@whiskeysockets/baileys');
const Database = require('better-sqlite3');
const fs = require('fs');
const { pipeline } = require('stream/promises');

async function main() {
  const db = new Database('$HOME/.openclaw/data/whatsapp-history.db', { readonly: true });
  const row = db.prepare('SELECT raw_json FROM messages WHERE id = ?').get('MESSAGE_ID_HERE');
  const msg = JSON.parse(row.raw_json);
  const audioMsg = msg.message.audioMessage;
  const stream = await downloadContentFromMessage(audioMsg, 'audio');
  await pipeline(stream, fs.createWriteStream('/tmp/voice-msg.ogg'));
  console.log('Downloaded!');
}
main().catch(console.error);
"
```

3. **Transcribe with Whisper** (or any STT):

```bash
ffmpeg -i /tmp/voice-msg.ogg -ar 16000 -ac 1 /tmp/voice-msg.wav -y
whisper /tmp/voice-msg.wav --model base --language es --output_format txt --output_dir /tmp/
cat /tmp/voice-msg.txt
```

### Download Other Media Types

Same pattern, different message field and content type:

| Media Type  | Proto Field       | Content Type |
| ----------- | ----------------- | ------------ |
| Voice/Audio | `audioMessage`    | `"audio"`    |
| Image       | `imageMessage`    | `"image"`    |
| Video       | `videoMessage`    | `"video"`    |
| Document    | `documentMessage` | `"document"` |
| Sticker     | `stickerMessage`  | `"sticker"`  |

Example for images:

```javascript
const imgMsg = msg.message.imageMessage;
const stream = await downloadContentFromMessage(imgMsg, "image");
await pipeline(stream, fs.createWriteStream("/tmp/photo.jpg"));
```

### Important Notes

- **Media URLs expire** — WhatsApp CDN links are temporary. Download soon after receiving, or Baileys will attempt a re-upload request (which requires an active socket connection).
- **Active WhatsApp session recommended** — If the media URL has expired, Baileys needs the socket to request a fresh URL. Works best when WhatsApp is connected.
- **Database path:** `~/.openclaw/data/whatsapp-history.db`
- **Source dir required:** The download script needs Baileys (`@whiskeysockets/baileys`) and `better-sqlite3`, both available in the OpenClaw source tree.

### Use Cases

- Transcribe voice messages from group chats you monitor
- Save important images/documents shared in groups
- Create searchable transcripts of voice-heavy conversations
- Analyze audio messages in languages you don't speak (Whisper supports 99 languages)

---

## Full History Resync (v1.5.0+)

Pull your **entire WhatsApp message history** — months or years of messages — into the local database. This works by re-linking your WhatsApp device, which triggers WhatsApp's INITIAL_BOOTSTRAP sync (the same sync that happens when you first link a new device).

### Why?

WhatsApp's on-demand history fetch (`fetchMessageHistory`) is broken in Baileys (see [Issue #1934](https://github.com/WhiskeySockets/Baileys/issues/1934)). The only reliable way to get old messages is through the initial device link sync. This feature automates the entire process safely.

### How It Works

```
Agent triggers resync → Auth cleared (backup saved) → Listener closed
→ Gateway enters QR wait loop → User scans QR in webchat Channels tab
→ WhatsApp sends INITIAL_BOOTSTRAP → Live capture stores everything to SQLite
```

### Setup

Install the `whatsapp-resync` plugin:

1. Copy the plugin to `~/.openclaw/extensions/whatsapp-resync/`
2. Add to `openclaw.json`:

```json
{
  "plugins": [{ "name": "whatsapp-resync", "path": "~/.openclaw/extensions/whatsapp-resync" }]
}
```

3. Restart the gateway.

### Endpoints

| Endpoint                       | Method | Description                                                        |
| ------------------------------ | ------ | ------------------------------------------------------------------ |
| `/api/whatsapp/resync`         | POST   | Trigger resync: backs up auth, clears credentials, closes listener |
| `/api/whatsapp/resync/restore` | POST   | Restore from backup if something goes wrong                        |

### Trigger a Resync

```bash
curl -X POST http://localhost:3120/api/whatsapp/resync
```

Response:

```json
{
  "ok": true,
  "message": "WhatsApp auth cleared and listener closed...",
  "backupDir": "~/.openclaw/credentials/whatsapp/default.resync-backup.2026-02-13T15-11-32",
  "filesDeleted": 3532
}
```

### Complete the Re-link

1. Open the webchat → **Channels** tab → scan the QR code with your phone
2. On your phone: WhatsApp → Settings → Linked Devices → Link a Device
3. Scan the QR code
4. Wait for the initial sync to complete (1-5 minutes depending on history size)

### Verify Results

```
whatsapp_history action=stats
```

A successful resync typically pulls thousands of messages spanning months or years.

### Restore from Backup

If something goes wrong, restore the previous auth state:

```bash
# Restore latest backup
curl -X POST http://localhost:3120/api/whatsapp/resync/restore

# Restore specific backup
curl -X POST http://localhost:3120/api/whatsapp/resync/restore \
  -H 'Content-Type: application/json' \
  -d '{"backupDir": "/path/to/backup"}'
```

### Safety

- **Automatic backup**: Auth credentials are backed up before deletion
- **No data loss**: Only auth state is cleared; existing messages in SQLite are preserved
- **Restore endpoint**: One-click rollback to previous state
- **Non-destructive**: Your WhatsApp account is unaffected; only the linked device session changes

### Real-World Results

In testing, a resync pulled:

- **17,609 messages** (up from 3,242)
- **1,229 chats** (up from 57)
- **4,077 contacts**
- History spanning **3+ years** (back to September 2022)

---

## Offline Message Recovery (v1.6.0+)

When the gateway goes down (restart, crash, update), messages sent during downtime aren't lost — they're stored by WhatsApp and delivered as a batch on reconnect. OpenClaw now recovers these automatically.

### How It Works

1. Gateway reconnects to WhatsApp (Baileys)
2. WhatsApp delivers missed messages as `append`-type events (history catch-up)
3. OpenClaw checks each message's timestamp against a recovery window (default: **6 hours**)
4. Messages within the window pass through normal access control and are processed as if they arrived in real-time
5. Messages older than the window are marked as read but not processed (prevents replaying ancient history)

### What This Means

- **Gateway down for minutes or hours?** All messages recovered automatically on reconnect
- **Self-chat messages** (owner talking to themselves) are recovered just like any other message
- **Access control still applies** — unauthorized senders are still filtered
- **Deduplication still applies** — no double-processing of messages

### Configuration

The recovery window defaults to 6 hours. This can be adjusted via the `offlineRecoveryMs` parameter in the monitor options. Set to `0` to disable recovery entirely (original behavior).

### Smart Recovery (Review Before Action)

Recovered messages are tagged with `[OFFLINE RECOVERY]` so the agent knows they're from a backlog. Instead of blindly acting on each message:

1. **All recovered messages are read first** — the agent gathers full context
2. **A summary is provided** — "While I was offline, you sent X messages about Y"
3. **Confirmation is requested** — "Would you like me to proceed with Z, or has this been resolved?"

This prevents duplicate actions, outdated requests being executed, and the chaos of responding to a backlog message-by-message.

### Tips

- If your gateway has scheduled restarts (e.g., for updates), keep them short — all messages within the 6h window are recovered
- The recovery window is generous by default; most gateway downtime is measured in seconds or minutes
- Messages older than the window are still stored in the history database — use `whatsapp_history` search to find them

---

## Voice Note Transcription & Prefix Matching (v1.7.0+)

Voice notes are now first-class citizens in the WhatsApp pipeline. When a voice note arrives, it's transcribed **before** any prefix checking, so `triggerPrefix` works naturally with spoken messages.

### How It Works

```
Voice note arrives → Download OGG → Transcribe (OpenAI Whisper) → Check triggerPrefix → Process
```

1. Audio downloaded and saved to `~/.openclaw/media/inbound/`
2. Transcribed via configured audio provider (OpenAI Whisper by default)
3. Transcript checked against `triggerPrefix` (e.g., must start with "Jarvis")
4. If prefix matches, transcript replaces `<media:audio>` body and enters the agent session
5. Agent sees the spoken text, not a placeholder

### Configuration

Enable audio transcription in `openclaw.json`:

```json
{
  "tools": {
    "media": {
      "audio": {
        "enabled": true
      }
    }
  }
}
```

### Prefix Matching

The same `triggerPrefix` rules apply to voice as to text:

- ✅ "Jarvis, what time is it?" → triggers (starts with "Jarvis")
- ❌ "Hey Jarvis, what time is it?" → does NOT trigger (starts with "Hey")
- ❌ "Tell Jarvis to..." → does NOT trigger

### Echo Prevention

Bot-sent voice notes (TTS replies) are tracked by message ID and automatically filtered out on re-ingestion. This prevents the bot from responding to its own voice replies — especially important during gateway restarts when append messages are recovered.

---

## Metallic Voice Replies (v1.7.0+)

Send voice note replies with a JARVIS-inspired metallic voice using local TTS (sherpa-onnx + ffmpeg effects). Zero cloud costs, zero latency.

### Setup

1. Install sherpa-onnx TTS (see `sherpa-onnx-tts` skill)
2. Create the `jarvis-wa-tts` script:

```bash
#!/bin/bash
# Usage: jarvis-wa-tts "text" [output.ogg]
TEXT="$1"
OUTPUT="${2:-/tmp/jarvis-wa-tts-output.ogg}"
RAW_WAV="/tmp/jarvis-wa-tts-raw.wav"
SHERPA_DIR="$HOME/.openclaw/tools/sherpa-onnx-tts"
MODEL_DIR="$SHERPA_DIR/models/vits-piper-en_GB-alan-medium"
export LD_LIBRARY_PATH="$SHERPA_DIR/lib:$LD_LIBRARY_PATH"

"$SHERPA_DIR/bin/sherpa-onnx-offline-tts" \
  --vits-model="$MODEL_DIR/en_GB-alan-medium.onnx" \
  --vits-tokens="$MODEL_DIR/tokens.txt" \
  --vits-data-dir="$MODEL_DIR/espeak-ng-data" \
  --vits-length-scale=0.5 \
  --output-filename="$RAW_WAV" "$TEXT" >/dev/null 2>&1

ffmpeg -y -i "$RAW_WAV" \
  -af "asetrate=22050*1.05,aresample=22050,flanger=delay=0:depth=2:regen=50:width=71:speed=0.5,aecho=0.8:0.88:15:0.5,highpass=f=200,treble=g=6" \
  -c:a libopus -b:a 64k "$OUTPUT" -v error
rm -f "$RAW_WAV"
echo "$OUTPUT"
```

3. Make executable: `chmod +x ~/.local/bin/jarvis-wa-tts`

### Usage in Agent

```bash
# Generate voice note
jarvis-wa-tts "Hello sir, systems nominal." /tmp/reply.ogg

# Send as WhatsApp voice note
message action=send channel=whatsapp target="+1234567890" filePath=/tmp/reply.ogg asVoice=true
```

### Effects Chain

- **Speed:** 2x (vits-length-scale=0.5)
- **Pitch:** +5% (asetrate)
- **Flanger:** Metallic shimmer
- **Echo:** 15ms short delay
- **EQ:** High-pass 200Hz + treble boost +6dB

---

## Troubleshooting

### Messages from family/friends not reaching agent

**Symptom:** You added someone to `groupAllowFrom` but their DMs don't work.

**Fix:** Add them to `allowFrom` too. `groupAllowFrom` only controls group message access, not DMs.

```json
{
  "allowFrom": ["+34612345678", "+14155551234"],
  "groupAllowFrom": ["+34612345678", "+14155551234"]
}
```

### Can't tell who sent which message in a DM

**Symptom:** All messages in a DM conversation show the same phone number.

**Cause:** Prior to OpenClaw 2026.2.1, DM messages showed the _chat ID_ (the other person's number) instead of the _actual sender_.

**Fix:** Update to latest OpenClaw. The agent now correctly distinguishes between messages you send and messages the other person sends in the same conversation.

### Voice notes won't play on WhatsApp

**Symptom:** Audio file sends but shows as unplayable.

**Fix:** Use OGG/Opus format, not MP3:

```bash
ffmpeg -i input.mp3 -c:a libopus -b:a 64k output.ogg
```

Then send with `asVoice=true`.

---

## Architecture

```
Your Agent
    ↓
OpenClaw message tool
    ↓
WhatsApp Channel Plugin
    ↓
Baileys (WhatsApp Web Protocol)
    ↓
WhatsApp Servers
```

No external services. No Docker. No CLI tools. Direct protocol integration.

---

## Credits

Created by **Oscar Serra** with the help of **Claude** (Anthropic).

_The skill that finally made WhatsApp work the way it should._

---

## License

MIT — Part of OpenClaw

---

## Links

- OpenClaw Fork: https://github.com/globalcaos/clawdbot-moltbot-openclaw
- Baileys: https://github.com/WhiskeySockets/Baileys
- ClawHub: https://clawhub.com
