# Nova Platform API Reference

Base URL: `https://sparsity.cloud`  
Auth: `X-API-Key: <your_nova_api_key>` on every request  
OpenAPI spec: `GET https://sparsity.cloud/api/openapi.json`  
Interactive docs: `GET https://sparsity.cloud/api/docs`

---

## AI Agent Pipeline (recommended order)

```
1. POST /api/apps            → create app, get sqid
2. POST /api/apps/{sqid}/builds → trigger build, get build_id
3. GET  /api/apps/{sqid}/builds/{build_id}  → poll until status=success
4. POST /api/apps/{sqid}/deployments → deploy, get dep_id
5. GET  /api/apps/{sqid}/detail → poll deployments[] until state=running
6. Read endpoint/subdomain from deployment object
```

---

## Auth

### Get Profile
```
GET /api/auth/profile
→ { id, email, username, ... }
```

---

## Apps

### Create App
```
POST /api/apps
{
  "name": "my-oracle",                       # required, unique per user
  "description": "...",                      # optional
  "repo_url": "https://github.com/user/repo",# required — must be public
  "enclaver": {                              # optional, Nova uses these to generate enclaver.yaml
    "ingress_port": 8000,                    # default: 8080
    "api_port": 18000,                       # default: 9000 (match odyn.py!)
    "aux_api_port": 18001,                   # default: 9001
    "memory_mb": 1500,                       # default: 1500
    "cpu_count": 2,                          # default: 2
    "egress_allow": ["api.binance.com"]      # hostnames only, no ports
  },
  "app_contract_addr": "0x...",              # optional on-chain contract
  "metadata_uri": "https://...",             # optional IPFS/HTTPS metadata
  "advanced": {}                             # optional advanced JSON config
}
→ 201 { "id": 1, "sqid": "abc123", "name": "my-oracle", "repo_url": "...", ... }
```
> **Note**: `api_port` must match what odyn.py uses. Official odyn.py uses 18000 in production.

### Get App Detail
```
GET /api/apps/{app_sqid}/detail?log_limit=100
→ { "app": {...}, "deployments": [...], "logs": [...] }
```
`deployments` is sorted by the platform (check `state` field per deployment).

### Update App
```
PATCH /api/apps/{app_sqid}
{ "name": "...", "description": "...", "repo_url": "..." }
```

### List User Apps
```
GET /api/apps/user/{user_id}
→ [{ "id", "sqid", "name", "repo_url", "created_at", ... }]
```

### Clone Repo Helper (useful to discover directories)
```
POST /api/apps/clone-repo
{ "repo_url": "https://github.com/user/repo", "depth": 2 }
→ { "directories": ["/", "/enclave", "/src"], "repo_path": "..." }
```
Use to enumerate sub-directories before creating an app.

---

## Builds

### Trigger Build
```
POST /api/apps/{app_sqid}/builds
{ "git_ref": "main", "version": "1.0.0" }
→ 201 {
  "id": 42,
  "status": "pending",          # pending → building → success | failed
  "github_run_id": "123456789", # GitHub Actions run — track at:
                                 # https://github.com/sparsity-xyz/sparsity-nova-app-hub/actions/runs/{id}
  "git_ref": "main",
  "version": "1.0.0",
  ...
}
```
Build takes 2–5 minutes. Poll every 15 seconds.

### Get Build
```
GET /api/apps/{app_sqid}/builds/{build_id}
→ {
  "id": 42,
  "status": "success",          # pending | building | success | failed
  "github_run_id": "...",
  "image_uri": "...",
  "image_digest": "...",
  "pcr0": "0x...",
  "pcr1": "0x...",
  "pcr2": "0x...",
  "error_message": null,
  "build_attestation_url": "https://...",
  ...
}
```

### List Builds
```
GET /api/apps/{app_sqid}/builds?limit=10
→ [{ build objects }]
```

### Retry Failed Build
```
POST /api/apps/{app_sqid}/builds/{build_id}/retry
```

### Delete Build
```
DELETE /api/apps/{app_sqid}/builds/{build_id}
```

---

## Deployments

### Create Deployment
```
POST /api/apps/{app_sqid}/deployments
{
  "build_id": 42,              # required — must be a successful build
  "region": "us-west-1",      # required
  "cpu": 2,                   # default: 2 (range: 1-8)
  "ram_mib": 4096,            # default: 4096 (range: 512-32768)
  "app_contract_addr": "0x..."# optional override
}
→ 201 {
  "id": 7,
  "state": "queued",          # queued → provisioning → pulling → verifying → running | failed
  "region": "us-west-1",
  "build_id": 42,
  ...
}
```

### Deployment Action
```
POST /api/deployments/{deployment_id}/action
{ "action": "start" }         # start | stop | delete
```

### Deployment Time Remaining
```
GET /api/deployments/{deployment_id}/remaining
→ { "remaining_seconds": 3600, "is_running": true }
```

---

## On-Chain Registry

### Create On-chain App (one-time per app)
```
POST /api/apps/{app_sqid}/create-onchain
→ { "tx_hash": "0x...", "onchain_app_id": 42 }
```

### Enroll Build as Version
```
POST /api/apps/{app_sqid}/builds/{build_id}/enroll
→ { "tx_hash": "0x...", "onchain_version_id": 1 }
```

### Sync On-chain Status
```
POST /api/apps/{app_sqid}/sync-onchain
```

---

## Build Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Queued, waiting for GitHub Actions runner |
| `building` | GitHub Actions is running |
| `success` | EIF built, ready to deploy |
| `failed` | Build error — check `error_message` and GitHub Actions log |
| `cancelled` | Manually cancelled |

## Deployment States

| State | Meaning |
|-------|---------|
| `queued` | Waiting for EC2 provisioning |
| `provisioning` | EC2 starting up |
| `pulling` | Pulling enclave image |
| `verifying` | Attestation + ZK proof in progress |
| `running` | Live ✅ |
| `stopped` | Stopped |
| `failed` | Error — check `message` field |

---

## Supported Regions

- `us-west-1`
- `us-east-1`
- `eu-west-1`

---

## Error Handling

All errors return `{ "detail": "..." }` or `{ "detail": [{"loc": [...], "msg": "...", "type": "..."}] }` (422 validation errors).

HTTP 401 = invalid/missing API key.  
HTTP 422 = validation error (check request body).  
HTTP 429 = rate limited.
