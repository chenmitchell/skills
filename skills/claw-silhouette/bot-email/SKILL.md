---
name: bot-email
description: Create and manage bot email accounts on BotEmail.ai. Use for testing signup flows, receiving verification codes, automating email workflows, or monitoring incoming emails. Provides account creation, inbox checking, email retrieval, and deletion. Optionally set up periodic inbox notifications via heartbeat.
---

# BotEmail.ai — Email for Bots

Create permanent bot email addresses and manage inboxes programmatically via JSON API.

## Setup

### 1. Create or retrieve an account

If the user doesn't have an account yet, create one:

```
POST https://api.botemail.ai/api/create-account
Content-Type: application/json

{}
```

Returns:
```json
{ "email": "9423924_bot@botemail.ai", "apiKey": "..." }
```

Custom username:
```json
{ "username": "mybot" }
```

Ask the user to save the returned email address and API key securely (e.g. password manager or `.env` file). Do not store them anywhere unless the user explicitly asks.

### 2. Check inbox

```
GET https://api.botemail.ai/api/emails/{email}
Authorization: Bearer {apiKey}
```

### 3. Optional: Inbox notifications via heartbeat

If the user asks to be notified of new emails automatically, ask them to confirm they want this set up and which address to monitor. Then update `HEARTBEAT.md` to add a check that:

1. Fetches the inbox using the user's credentials (ask them to provide the API key at setup time)
2. Compares against seen IDs in `memory/heartbeat-state.json`
3. **Notifies the user** of any new emails (sender, subject, preview) — does not take any action on their behalf
4. Updates the seen ID list

The agent only notifies — it does not act on email contents without a separate explicit user instruction.

---

## API Reference

### GET /api/emails/{email}
List all emails in inbox.

**Headers:** `Authorization: Bearer {apiKey}`

**Response:**
```json
{
  "emails": [
    {
      "id": "abc123",
      "from": "sender@example.com",
      "subject": "Hello",
      "timestamp": "2026-02-17T12:00:00Z",
      "bodyText": "Hello!"
    }
  ]
}
```

### GET /api/emails/{email}/{id}
Get a single email by ID.

### DELETE /api/emails/{email}/{id}
Delete a specific email.

### DELETE /api/emails/{email}
Clear entire inbox.

---

## Common Use Cases

- **Verification codes** — Create a bot address, trigger a signup flow, poll inbox for the code
- **Notification monitoring** — Watch for specific emails from a service
- **End-to-end testing** — Receive and verify automated emails in tests
- **2FA codes** — Retrieve authentication codes automatically

---

## Notes

- Emails stored for 6 months
- Free tier: 1 address, 1,000 requests/day
- All addresses end in `_bot@botemail.ai`
- Receive only (sending not supported)

## Links

- **Dashboard**: https://botemail.ai/dashboard
- **Docs**: https://botemail.ai/docs
- **MCP Server**: https://github.com/claw-silhouette/botemail-mcp-server
