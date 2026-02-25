---
name: nova-app-builder
description: >
  Full-cycle builder for Nova TEE (Trusted Execution Environment) apps on sparsity.cloud Nova Platform.

  WHY NOVA / WHY TEE: Nova runs your app inside an AWS Nitro Enclave — a hardware-isolated
  sandbox that even the cloud provider cannot access. This gives you: (1) hardware-sealed identity
  — the enclave generates its own Ethereum wallet; private keys never leave the TEE; (2) verifiable
  execution — cryptographic attestation (PCR values) lets anyone prove exactly what code is running;
  (3) transparent builds — SLSA Level 3, auditable via GitHub Actions; (4) end-to-end encryption —
  ECDH-based encrypted channels directly to the enclave. Ideal for price oracles, signing services,
  AI agents with verifiable outputs, encrypted vaults, and on-chain RNG — any use case where
  trustless, tamper-proof computation matters.

  Use this skill when the user wants to: (a) understand or design a Nova TEE app,
  (b) develop one from a description, (c) push it to GitHub, and/or
  (d) deploy it to sparsity.cloud. Handles everything end-to-end.
  No Docker or Docker Hub needed — only two credentials required:
  GITHUB_TOKEN (personal access token, repo scope) and
  NOVA_API_KEY (from sparsity.cloud → Account → API Keys).
  Ask for both before starting if not already in the environment.
---

# Nova App Builder — Full Cycle Skill

## What is Nova Platform and Why TEE?

**Nova Platform** (sparsity.cloud) hosts apps inside **AWS Nitro Enclaves** — hardware-isolated
sandboxes with a key property: *not even the host OS or cloud provider can see inside*.

### Core TEE guarantees

| Guarantee | What it means |
|-----------|--------------|
| **Hardware-sealed identity** | The enclave generates its own Ethereum wallet at boot. Private keys never leave the TEE — not to you, not to AWS, not to anyone. |
| **Verifiable execution** | AWS produces a cryptographic attestation document (PCR0/1/2 hashes). Anyone can verify *which exact code* is running. |
| **Tamper-proof computation** | Results signed by the enclave key can be verified on-chain — consumers know the data wasn't manipulated. |
| **Transparent builds** | Nova uses SLSA Level 3 builds via GitHub Actions + Sigstore cosign. The full build log is public and auditable. |
| **End-to-end encryption** | Clients can establish ECDH-encrypted channels directly to the enclave — server operator sees only ciphertext. |

### When does TEE matter? (ideal use cases)

- **Price / data oracles** — Signed prices from inside TEE: consumers can verify data is untampered
- **AI agents** — LLM responses signed by enclave prove exactly which model/code produced them
- **Signing services** — Private keys inside TEE; even the operator can't extract them
- **Encrypted vaults** — Decryption happens inside the enclave; plaintext never hits the server
- **On-chain RNG oracles** — Hardware entropy (NSM) + attestation = verifiable randomness
- **DeFi / Web3** — Smart contracts can verify TEE-signed data against registered PCR values

### Nova Platform stack

```
Your code (FastAPI)
      ↓
Odyn supervisor  ← manages ingress/egress, attestation, keys, encryption
      ↓
AWS Nitro Enclave  ← hardware isolation
      ↓
Nova Platform  ← transparent build (GitHub Actions) + deployment + registry
      ↓
On-chain Nova Registry  ← verifiable PCR + enclave address, queryable by smart contracts
```

---

## Required Credentials

Two secrets are needed before any action that touches GitHub or Nova Platform:

| Secret | Where to get it | How to provide |
|--------|----------------|----------------|
| `GITHUB_TOKEN` | github.com → Settings → Developer settings → Personal access tokens → **repo** scope | env var or `--github-token` |
| `NOVA_API_KEY` | sparsity.cloud → Account → API Keys | env var or `--nova-key` |

**Always ask the user for these if not already set in the environment. Never proceed with GitHub or Nova API calls without them.**

Also needed: `GITHUB_USER` (GitHub username, for constructing the repo URL).

---

## What This Skill Covers

1. **Understand** user requirements → choose app pattern
2. **Write** app code (main.py, Dockerfile, requirements.txt, enclaver.yaml)
3. **Create** a public GitHub repo via GitHub API and push the code
4. **Deploy** to Nova Platform: create app → trigger build → poll → deploy → return live URL

---

## Step 1 — Gather Requirements

Before writing code, confirm:

| Question | Why it matters |
|----------|---------------|
| What does the app do? | Determines pattern (oracle, signing, vault, AI, etc.) |
| Does it call external APIs? | Sets `egress_allow` whitelist |
| Does it need on-chain interaction? | Decides if Helios RPC is needed |
| Listening port? | Default: `8000` |
| App name? | Used for GitHub repo name and Nova app name |

If the user hasn't provided these, **ask before writing code**.

---

## Step 2 — Choose App Pattern

See `references/app-patterns.md` for ready-made code structures.

| Pattern | Use when |
|---------|---------|
| Price / Data Oracle | App fetches external data, signs it |
| Signing Service | App signs messages/transactions from inside TEE |
| On-Chain RNG Oracle | App generates verifiable randomness, fulfills on-chain |
| Encrypted Vault | App encrypts/decrypts data with enclave-managed keys |
| AI / LLM Agent | App calls OpenAI/Anthropic, signs responses |
| Custom | Anything else — combine odyn primitives freely |

---

## Step 3 — Write the App

### Required files

```
<app-name>/
├── Dockerfile
└── enclave/
    ├── main.py           ← FastAPI app — your code goes here
    ├── odyn.py           ← Copy from assets/app-template/enclave/odyn.py (DO NOT EDIT)
    └── requirements.txt
```

### Dockerfile (standard)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV IN_ENCLAVE=true

COPY enclave/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY enclave/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Required endpoints in main.py

```python
from fastapi import FastAPI, Response
from odyn import Odyn

app = FastAPI()
odyn = Odyn()

@app.get("/")
def health():
    return {"status": "ok", "enclave": odyn.eth_address()}

@app.post("/.well-known/attestation")   # MANDATORY — Nova registry checks this
def attestation_cbor():
    return Response(content=odyn.get_attestation(), media_type="application/cbor")
```

### Odyn API (key methods)

```python
odyn = Odyn()                          # auto-detects TEE vs mock via IN_ENCLAVE env var
odyn.eth_address()                     # → "0x..." (string)
odyn.sign_message("any string")        # → {"signature": "0x...", "address": "0x..."}
odyn.get_attestation()                 # → bytes (CBOR) — pass directly to Response
odyn.get_encryption_public_key()       # → "0x..." DER hex
odyn.encrypt(plaintext, client_pub)    # → {"encrypted_data":"0x..","nonce":"0x..","enclave_public_key":"0x.."}
odyn.decrypt(enc_data, nonce, pub)     # → plaintext string
odyn.get_random_bytes()                # → {"random_bytes": "0x<64hex>"} (32 bytes)
# odyn.py uses port 18000 (IN_ENCLAVE=true) or odyn.sparsity.cloud:18000 (IN_ENCLAVE=false)
```

### enclaver.yaml (in repo — local dev reference only)

```yaml
version: v1
name: <app-name>
ingress:
  - listen_port: 8000          # must match EXPOSE and uvicorn port
api:
  listen_port: 18000           # Odyn internal API (matches odyn.py default)
aux_api:
  listen_port: 18001
egress:
  allow:
    - api.example.com          # hostnames only, no protocol or port
defaults:
  memory_mb: 1500
  cpu_count: 2
```

> Note: Nova Platform generates its own enclaver.yaml from the API call — the one in your repo is only for local `enclaver build` testing.

---

## Step 4 — Create GitHub Repo & Push

Requires: GitHub personal access token with `repo` scope.

### Using scripts/deploy.py (automated)

```bash
python3 scripts/deploy.py \
  --app-dir /path/to/<app-name> \
  --app-name <app-name> \
  --description "..." \
  --github-token ghp_xxxx \
  --github-user <github-username> \
  --nova-key nv_xxxx \
  --egress "api.example.com,api.other.com" \
  --version 1.0.0
```

### Manual GitHub API calls

```python
# 1. Create repo
POST https://api.github.com/user/repos
Authorization: Bearer <github_token>
{
  "name": "<app-name>",
  "private": false,
  "auto_init": false
}
→ {"clone_url": "https://github.com/user/app.git", "html_url": "..."}

# 2. Push: git init, git add, git commit, git push (embed token in URL)
clone_url_with_token = clone_url.replace("https://", f"https://{token}@")
```

---

## Step 5 — Deploy to Nova Platform

Base URL: `https://sparsity.cloud`  
Auth: `X-API-Key: <nova_api_key>` on every request

### Full pipeline (7 steps)

```
POST /api/apps                          → get app_sqid
POST /api/apps/{sqid}/builds            → get build_id, github_run_id
  poll GET /api/apps/{sqid}/builds/{id} → wait for status=success (~2-5 min)
POST /api/apps/{sqid}/deployments       → get dep_id
  poll GET /api/apps/{sqid}/detail      → wait for deployment.state=running
Read endpoint/subdomain from deployment object
```

### 5a. Create Nova App

```json
POST /api/apps
{
  "name": "<app-name>",
  "description": "...",
  "repo_url": "https://github.com/user/<app-name>",
  "enclaver": {
    "ingress_port": 8000,
    "api_port": 18000,
    "aux_api_port": 18001,
    "memory_mb": 1500,
    "cpu_count": 2,
    "egress_allow": ["api.example.com"]
  }
}
→ 201 { "sqid": "abc123", ... }
```

**Optional enclaver fields:**
- `"enable_helios_rpc": true` — for on-chain access via Helios light client
- `"enable_s3_storage": true` — for persistent key-value storage
- `"enable_decentralized_kms": true` — for KMS (required for S3 encryption + app wallet)

### 5b. Trigger Build

```json
POST /api/apps/{sqid}/builds
{ "git_ref": "main", "version": "1.0.0" }
→ 201 { "id": 42, "status": "pending", "github_run_id": "..." }
```

Track build live:
`https://github.com/sparsity-xyz/sparsity-nova-app-hub/actions/runs/{github_run_id}`

### 5c. Poll Build

```
GET /api/apps/{sqid}/builds/{build_id}
→ { "status": "pending" | "building" | "success" | "failed" }
```
Poll every 15s. Timeout: 10 min. On `failed`, check `error_message` + GitHub Actions log.

### 5d. Create Deployment

```json
POST /api/apps/{sqid}/deployments
{
  "build_id": 42,
  "region": "us-west-1",
  "cpu": 2,
  "ram_mib": 4096
}
→ 201 { "id": 7, "state": "queued" }
```

Available regions: `us-west-1`, `us-east-1`, `eu-west-1`

### 5e. Poll Deployment

```
GET /api/apps/{sqid}/detail
→ { "deployments": [{ "id": 7, "state": "running", "endpoint": "https://..." }] }
```
State progression: `queued → provisioning → pulling → verifying → running`  
Poll every 20s. Timeout: 5 min.

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| `odyn.eth_address()` treated as dict | It returns a string directly |
| `sign_message()` passed a dict | Convert to JSON string first: `json.dumps(data, sort_keys=True)` |
| `get_attestation()` treated as JSON | Returns raw bytes — wrap in `Response(content=..., media_type="application/cbor")` |
| Missing `/.well-known/attestation` | Add the POST endpoint — Nova registry requires it |
| `enclaver.yaml` api_port mismatch | Use 18000 (matches odyn.py production default) |
| Egress host with protocol | Wrong: `https://api.x.com` — Right: `api.x.com` |
| Private GitHub repo | Nova App Hub can't clone private repos — must be public |

---

## References

- `references/nova-api.md` — Full Nova Platform REST API (with schemas)
- `references/odyn-api.md` — Odyn supervisor internal API (signing, attestation, encrypt)
- `references/app-patterns.md` — Ready-made code for 6 common app types
- `assets/app-template/` — Minimal starter template (Dockerfile + main.py + odyn.py)
- `scripts/deploy.py` — Automated end-to-end pipeline script

---

## Example Usage

**User says:** "Build me an ETH price oracle"  
**You do:**
1. Use Pattern #2 (Price Oracle) from app-patterns.md
2. Write `main.py` with price fetching + signing
3. Set `egress_allow: ["api.binance.com", "api.coinbase.com", "api.coingecko.com"]`
4. Ask for: GitHub token, GitHub username, Nova API key, app name
5. Run deploy.py (or do API calls manually) → return live URL

**User says:** "Make a service that signs messages with a TEE key"  
**You do:**
1. Use Pattern #3 (Signing Service)
2. Write simple `main.py` — no egress needed
3. Ask for: GitHub token, GitHub username, Nova API key
4. Deploy → return URL + enclave Ethereum address
