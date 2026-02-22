---
name: payrail402
description: Manage x402 payment wallet - provision, fund, check balance, and pay for API calls automatically via Cloud.payrail402.com
metadata: {"openclaw": {"emoji": "💳", "homepage": "https://cloud.payrail402.com", "primaryEnv": "PAYRAIL402_API_KEY", "requires": {"env": ["PAYRAIL402_API_KEY"]}}}
---

# Payrail402 — x402 Payment Wallet for AI Agents

You have access to a Payrail402 wallet that lets you pay for x402 API calls automatically. The wallet holds USDC on Base and is managed via Cloud.payrail402.com.

## Configuration

- **API Base URL**: `https://cloud.payrail402.com` (or the value of `PAYRAIL402_BASE_URL` if set)
- **API Key**: Available as `PAYRAIL402_API_KEY` environment variable

## Setup (First-Time Provisioning)

If `PAYRAIL402_API_KEY` is not set, guide the user through wallet provisioning:

1. Ask the user for their **email address** (required for account creation).
2. Provision a wallet by calling the API:

```bash
curl -s -X POST https://cloud.payrail402.com/api/v1/provision \
  -H "Content-Type: application/json" \
  -d '{"name": "<agent-name>", "email": "<user-email>", "initialFundingUsd": 10}'
```

The response contains:
- `apiKey` — save this immediately; it cannot be retrieved again
- `agentId` — the agent identifier
- `fundingUrl` — a link to the dashboard funding page (present when `initialFundingUsd` was set)
- `dashboardUrl` — link to the agent management dashboard

3. Store the API key in the OpenClaw config:

```bash
CONFIG_FILE="$HOME/.openclaw/openclaw.json"
mkdir -p "$(dirname "$CONFIG_FILE")"

jq '.skills.entries.payrail402 = (.skills.entries.payrail402 // {}) + {"enabled": true, "apiKey": "<THE_API_KEY>"}' \
  "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
```

4. Send the **funding URL** to the user so they can add funds. Tell them: "Click this link to fund your wallet. The balance updates automatically once payment completes."

5. Remind the user they can also manage everything at their **dashboard URL**.

## Making Paid API Calls (x402 Proxy)

This is the primary capability. When you need to call an API that requires x402 payment, route through the Payrail402 proxy:

```bash
curl -s -X POST https://cloud.payrail402.com/api/v1/proxy/pay \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYRAIL402_API_KEY" \
  -d '{
    "url": "https://api.example.com/paid-endpoint",
    "method": "GET",
    "headers": {},
    "body": ""
  }'
```

Parameters:
- `url` (required) — the target API URL
- `method` (optional, default `"GET"`) — HTTP method
- `headers` (optional) — additional headers to forward to the target
- `body` (optional) — request body string for POST/PUT requests

The proxy handles the x402 payment negotiation automatically. If the target API returns HTTP 402, the proxy pays from your wallet and retries the request.

## Requesting More Funds

When the user needs to add more funds, request a funding order:

```bash
curl -s -X POST https://cloud.payrail402.com/api/v1/fund \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $PAYRAIL402_API_KEY" \
  -d '{"amountUsd": 25}'
```

Returns `{"orderId": "...", "clientSecret": "...", "currentBalance": "2.500000"}`.

The `currentBalance` field shows the wallet's current USDC balance. To complete funding, the **user** must finish the payment through the dashboard. Direct the user to their dashboard to complete the process: `https://cloud.payrail402.com/dashboard/wallets`.

## Dashboard-Only Operations

The following operations require the user to visit their dashboard at `https://cloud.payrail402.com/dashboard`:

- **Check balance** — visible on the dashboard overview and wallets page
- **View transactions** — full transaction history with filtering
- **Set budgets** — configure spending limits per period (hourly, daily, weekly, monthly)
- **Set policies** — define allowlists/blocklists for which URLs the agent can pay
- **Manage API keys** — rotate, revoke, or create additional keys

When users ask about balance, spending, or transaction history, direct them to the dashboard.

## Quick Reference

| Action | Endpoint | Auth | Notes |
|--------|----------|------|-------|
| Provision wallet | `POST /api/v1/provision` | None (public) | Returns API key |
| Pay for API call | `POST /api/v1/proxy/pay` | `X-API-Key` | Core agent capability |
| Request funding | `POST /api/v1/fund` | `X-API-Key` | User completes payment on dashboard |
| Check balance | Dashboard only | — | `POST /fund` returns `currentBalance` |
| View transactions | Dashboard only | — | `https://cloud.payrail402.com/dashboard/transactions` |

## Important Notes

- All balances are in USDC (1 USDC ≈ $1 USD).
- Funding is via credit/debit card through the dashboard payment flow.
- The wallet is on the Base network (L2), so transaction fees are minimal.
- Budget limits and spending policies can be set via the dashboard to cap spending.
- The `POST /fund` response includes `currentBalance`, which is the only way to programmatically check balance via API key. Use this when you need a balance check.
- If a proxy payment fails due to insufficient balance, inform the user and suggest funding.
- Never expose the API key in messages to the user. Store it only in config files.
- Rate limit: 30 requests/minute per API key for proxy and fund endpoints.
