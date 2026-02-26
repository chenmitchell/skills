---
name: API (Stripe, OpenAI, Notion & 100+ more)
slug: api
version: 1.3.0
homepage: https://clawic.com/skills/api
description: Integrate 147 REST APIs with multi-account credential management. Payments, AI, CRM, DevOps, and more.
changelog: Consolidated 147 APIs into category files for easier discovery.
metadata: {"clawdbot":{"emoji":"🔌","requires":{"anyBins":["curl","jq"]},"os":["linux","darwin","win32"]}}
---

# API

Integrate any API fast. 147 services documented with authentication, endpoints, and gotchas.

## Setup

On first use, read `setup.md` for integration guidelines and credential setup.

## When to Use

User needs to integrate a third-party API. Agent provides:
- Authentication setup with multi-account support
- Endpoint documentation with curl examples
- Rate limits, pagination patterns, and gotchas
- Credential naming conventions for multiple accounts

## Architecture

```
apis/                    # API reference files by category
  ├── ai-ml.md           # OpenAI, Anthropic, Cohere, etc.
  ├── payments.md        # Stripe, PayPal, Square, etc.
  ├── communication.md   # Twilio, SendGrid, Slack, etc.
  └── ...

~/api/                   # User preferences (created on first use)
  ├── preferences.md     # Default account selection, language
  └── accounts.md        # Registry of configured accounts
```

## Quick Reference

| File | Purpose |
|------|---------|
| `setup.md` | First-time setup and guidelines |
| `credentials.md` | Multi-account credential system |
| `memory-template.md` | Memory template for preferences |
| `auth.md` | Authentication pattern traps |
| `pagination.md` | Pagination pattern traps |
| `resilience.md` | Retry and error handling |
| `webhooks.md` | Webhook security patterns |

## API Categories

| Category | File | APIs |
|----------|------|------|
| AI/ML | `apis/ai-ml.md` | anthropic, openai, cohere, groq, mistral, perplexity, huggingface, replicate, stability, elevenlabs, deepgram, assemblyai, together, anyscale |
| Payments | `apis/payments.md` | stripe, paypal, square, plaid, chargebee, paddle, lemonsqueezy, recurly, wise, coinbase, binance, alpaca, polygon |
| Communication | `apis/communication.md` | twilio, sendgrid, mailgun, postmark, resend, mailchimp, slack, discord, telegram, zoom |
| Realtime | `apis/realtime.md` | sendbird, stream-chat, pusher, ably, onesignal, courier, knock, novu |
| CRM | `apis/crm.md` | salesforce, hubspot, pipedrive, attio, close, apollo, outreach, gong |
| Marketing | `apis/marketing.md` | drift, crisp, front, customer-io, braze, iterable, klaviyo |
| Developer | `apis/developer.md` | github, gitlab, bitbucket, vercel, netlify, railway, render, fly, digitalocean, heroku, cloudflare, circleci, pagerduty, launchdarkly, split, statsig |
| Database | `apis/database.md` | supabase, firebase, planetscale, neon, upstash, mongodb, fauna, xata, convex, appwrite |
| Auth | `apis/auth-providers.md` | clerk, auth0, workos, stytch |
| Media | `apis/media.md` | cloudinary, mux, bunny, imgix, uploadthing, uploadcare, transloadit, vimeo, youtube, spotify, unsplash, pexels, giphy, tenor |
| Social | `apis/social.md` | twitter, linkedin, instagram, tiktok, pinterest, reddit, twitch |
| Productivity | `apis/productivity.md` | notion, airtable, google-sheets, google-drive, google-calendar, dropbox, linear, jira, asana, trello, monday, clickup, figma, calendly, cal, loom, typeform |
| Business | `apis/business.md` | shopify, docusign, hellosign, bitly, dub |
| Geo | `apis/geo.md` | openweather, mapbox, google-maps |
| Support | `apis/support.md` | intercom, zendesk, freshdesk, helpscout |
| Analytics | `apis/analytics.md` | mixpanel, amplitude, posthog, segment, sentry, datadog, algolia |

## How to Navigate API Files

Each category file contains multiple APIs and can be large. **DO NOT read the entire file.** Use this efficient approach:

1. **Read the index first** — Each file starts with an index table showing API names and line numbers
2. **Jump to specific API** — Use the line number to read only that API's section (typically 50-100 lines)
3. **Example workflow:**
   ```bash
   # 1. Find which file has the API (use API Categories table above)
   # 2. Read just the index (first 20 lines)
   head -20 apis/ai-ml.md
   # 3. Read specific API section using line numbers from index
   sed -n '119,230p' apis/ai-ml.md  # OpenAI starts at line 119
   ```

**CRITICAL:** Never read a full category file. Always use the index → jump to line approach.

## Core Rules

1. **Check API docs first** — Find the API in the category table above, then read that file's index to locate the specific API section.

2. **Use multi-account credentials** — Store credentials with naming format `{SERVICE}_{ACCOUNT}_{TYPE}`. Example: `STRIPE_PROD_API_KEY`, `STRIPE_TEST_API_KEY`, `STRIPE_CLIENT_ACME_API_KEY`.

3. **Always include Content-Type** — POST/PUT/PATCH requests need `Content-Type: application/json`. Omitting causes silent 415 errors on many APIs.

4. **Handle rate limits proactively** — Track `X-RateLimit-Remaining` header. Throttle before hitting 0, don't wait for 429. Respect `Retry-After` header.

5. **Validate response schema** — Some APIs return 200 with error in body. Always check response structure, not just status code.

6. **Use idempotency keys** — For payments and critical operations, include idempotency key to prevent duplicates on retry.

7. **Never log credentials** — Use environment variables directly. Never echo, print, or commit credentials to files.

## Credential Management

Use environment variables with multi-account naming convention:

```bash
# Set for current session
export STRIPE_PROD_API_KEY="sk_live_xxx"

# Use in API call
curl https://api.stripe.com/v1/charges -H "Authorization: Bearer $STRIPE_PROD_API_KEY"
```

**Naming format:** `{SERVICE}_{ACCOUNT}_{TYPE}`
- `STRIPE_PROD_API_KEY` — Production
- `STRIPE_TEST_API_KEY` — Development  
- `STRIPE_CLIENT_ACME_API_KEY` — Client project

See `credentials.md` for persistent storage options and multi-account workflows.

## Common Traps

- **Missing Content-Type** — POST without `Content-Type: application/json` causes silent 415 errors
- **API keys in URLs** — Query params get logged in access logs, always use headers
- **Ignoring pagination** — Most APIs default to 10-25 items, always paginate
- **Not handling 429** — Implement exponential backoff with jitter
- **Assuming 200 = success** — Check response body for error objects
- **No idempotency keys** — Retries cause duplicate charges/actions
- **Hardcoding credentials** — Use environment variables, never hardcode in source code

## External Endpoints

This skill documents how to call external APIs. Calls go directly from your machine to the API provider. No data is proxied or stored.

| Provider | Base URL | Auth |
|----------|----------|------|
| Various | See category files | API Key / OAuth |

## Security & Privacy

**Credentials:** Stored in environment variables with naming convention `{SERVICE}_{ACCOUNT}_{TYPE}`.

**Multi-account:** Each account isolated with unique environment variable names. Naming convention prevents conflicts.

**This skill does NOT:**
- Store credentials in files
- Make requests on your behalf
- Send data to any third party
- Proxy API calls

You control all API calls directly.

## Related Skills
Install with `clawhub install <slug>` if user confirms:

- `http` — HTTP request patterns and debugging
- `webhook` — Webhook handling and security
- `json` — JSON processing and jq patterns

## Feedback

- If useful: `clawhub star api`
- Stay updated: `clawhub sync`
