---
name: basemail
description: Give your AI Agent a real email address! BaseMail lets agents send/receive emails using their Web3 wallet identity. Basename holders get yourname@basemail.ai. Includes wallet generation for agents without one. No CAPTCHAs, no passwords — just sign and send.
---

# 📬 BaseMail - Email for AI Agents

**Your agent deserves an email address.**

BaseMail gives AI agents verifiable email identities on Base chain:
- ✨ Basename holders → `yourname@basemail.ai`  
- 🔗 Others → `0xwallet@basemail.ai`

No CAPTCHAs. No passwords. Wallet signature is identity.

## 🚀 Quick Start (3 Steps)

### 1️⃣ Setup Wallet

```bash
npm install ethers
node scripts/setup.js
```
> Don't have a wallet? This creates one for you!

### 2️⃣ Register

```bash
node scripts/register.js
# Or with Basename:
node scripts/register.js --basename yourname.base.eth
```

### 3️⃣ Send Email!

```bash
node scripts/send.js "friend@basemail.ai" "Hello!" "Nice to meet you 🦞"
```

## 📦 What's Included

| Script | Purpose |
|--------|---------|
| `setup.js` | Generate new wallet (if needed) |
| `register.js` | Register for @basemail.ai email |
| `send.js` | Send emails |
| `inbox.js` | Check inbox & read emails |

## 🔐 Security

- Private keys stored with chmod 600
- Mnemonic shown once — back it up!
- Tokens auto-refresh
- Nothing sensitive hardcoded

## 📍 Files Created

```
~/.basemail/
├── private-key    # Your wallet key (chmod 600)
├── wallet.json    # Wallet address
└── token.json     # Auth token (auto-managed)
```

## 🎨 Get a Pretty Email

Want `yourname@basemail.ai` instead of `0x...@basemail.ai`?

1. Get a Basename at https://www.base.org/names
2. Run: `node scripts/register.js --basename yourname.base.eth`

## 🔧 API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/start` | POST | Start SIWE auth |
| `/api/auth/verify` | POST | Verify wallet signature |
| `/api/register` | POST | Claim email address |
| `/api/register/upgrade` | PUT | Upgrade to Basename |
| `/api/send` | POST | Send email |
| `/api/inbox` | GET | List received emails |
| `/api/inbox/:id` | GET | Read email content |

**Full docs**: https://api.basemail.ai/api/docs

## 🌐 Links

- Website: https://basemail.ai
- API: https://api.basemail.ai
- Get Basename: https://www.base.org/names
