# SharePoint API Access (Extreme Security)

This guide documents a hardened approach for granting API access to **one SharePoint directory** with strict least-privilege controls.

## Scope and Security Reality

With Microsoft Graph app-only access, practical least-privilege is usually at **site level** via `Sites.Selected` (not true single-folder scope in the same straightforward way).

**Secure design pattern:**
- Isolate target directory into a **dedicated SharePoint site** (preferred) or dedicated library.
- Grant the app access only to that site via `Sites.Selected`.
- Keep all other tenant content out of reach.

---

## Live Rollout Status (Pitagone)

> Keep this section updated during implementation.

### Current target
- **Tenant:** `pitagone.com` (`894e5500-6b83-4c8e-b80d-2a46208b87bd`)
- **SharePoint Site:** `ciso-isolated-site-for-automation`
- **Site ID:** `pitagone.sharepoint.com,7034c36b-ff5b-462b-84c9-85c6042dc9dc,a0963c03-2337-4074-aac3-f51940799843`
- **Dedicated Document Library:** `api-files-for-automation`
- **Entra App Registration:** `sp-api-ciso-automation-prod`
- **App Client ID:** `60c39b19-c445-4fe9-9898-a66c46a69877`
- **Certificate Thumbprint:** `3BF7A08FEB025C43532C229F1B865FBFC17EC98A`
- **Key Vault:** `vault-ciso-automati-prod`
- **Certificate in Vault:** `sp-api-ciso-automation-prod-pfx`
- **Grant Role:** `read`
- **Grant Date:** 2026-02-23

### Progress checklist
- [x] Step 1: Dedicated site/library isolation completed
- [x] Step 2: Dedicated Entra app registration created (single-tenant)
- [x] Step 3: Certificate auth configured (no client secret)
  - [x] Step 3.1: Certificate pair generated (4096-bit RSA, 365-day validity)
  - [x] Step 3.2: Certificate uploaded to app registration (thumbprint visible)
  - [x] Step 3.3: PFX imported into Key Vault
  - [x] Step 3.4a: Key Vault secret IAM — personal user assigned (runtime identity TBD)
  - [x] Step 3.4b: Soft-delete + purge protection enabled
  - [x] Step 3.4c: Certificate expiry alerting (email 90 days before, contact configured)
  - [x] Step 3.4d: Key Vault networking — "All networks" (acceptable for dev; see TODOs)
  - [x] Validation: no client secret created
- [x] Step 4: Graph permission `Sites.Selected` added + admin consent
- [x] Step 5: Site-level app grant applied (read only)
- [ ] Step 6: Monitoring, alerting, and IR controls (deferred — see below)

---

## Maximum-Security Architecture (12 Steps)

### 1) Isolate data (blast-radius control)
1. Create a **dedicated SharePoint site collection** for this integration.
2. Create one document library (example: `api-files`).
3. Move only the required directory/data into this site/library.
4. Remove broad/default principals where possible.
5. Break inheritance where needed and keep explicit ACLs minimal.

**Outcome:** if the app is compromised, impact is limited to this isolated zone.

### 2) Create a dedicated identity (one app, one purpose)
1. Create a new Entra App Registration for this integration only.
2. Use clear naming, e.g. `sp-api-<env>-<purpose>`.
3. Set **single-tenant** unless multitenant is explicitly required.
4. Create separate app registrations for dev/stage/prod.
5. Document owner, purpose, expiry, and escalation contacts.

**Outcome:** no permission sharing across unrelated workloads.

### 3) Enforce strong auth (no client secrets)
1. Do **not** use client secrets.
2. Use **certificate-based auth** (or Managed Identity when hosted in Azure).
3. Generate certs in a secure process; prefer short validity.
4. Store private key in Azure Key Vault (HSM-backed if available).
5. Restrict Key Vault access with RBAC and network controls.
6. Enable rotation and pre-expiry alerting.

**Outcome:** removes password-like static credentials.

### 4) Apply least-privilege Graph permission
1. Add Microsoft Graph **Application** permission: `Sites.Selected` only.
2. Avoid `Sites.Read.All` and `Sites.ReadWrite.All`.
3. Grant admin consent only for required permission.
4. Validate effective permissions before production.

**Outcome:** app has zero SharePoint data access until site grant is explicit.

### 5) Grant access only to the target site
1. Identify exact target site ID.
2. Grant app to that site only (`read` role if possible, `write` only if needed).
3. Verify app cannot access other sites.
4. Record who approved and when (audit evidence).

**Outcome:** strict site boundary enforcement.

### 6) Lock down admin and consent process
1. Restrict admin consent rights to a small, controlled group.
2. Require approval workflow and justification for app consents.
3. Use PIM/JIT for privileged roles.
4. Require MFA + compliant device for admins.
5. Define and monitor break-glass admin policy.

**Outcome:** reduced risk of accidental/malicious privilege grant.

### 7) Conditional Access for workload identity
1. Create CA policy targeting this service principal (if supported in tenant/license).
2. Restrict to expected network/location conditions.
3. Block unsupported/legacy paths.
4. Start report-only, then enforce.

**Outcome:** valid credentials are less usable outside approved context.

### 8) Harden application/API code path
1. Enforce internal allowlist for tenant/site/library/path prefix.
2. Canonicalize and validate paths server-side (block traversal).
3. Default read-only; require explicit policy for write/delete.
4. Validate inputs and sanitize outputs.
5. Use bounded retries/timeouts.
6. Add rate limiting and abuse controls.
7. Never log tokens or secrets.

**Outcome:** prevents scope escape and common API abuse.

### 9) Encrypt and protect secrets end-to-end
1. TLS 1.2+ for all traffic.
2. Encrypt sensitive data at rest.
3. Pull secrets/certs only from Key Vault at runtime.
4. Use managed identity for vault access when possible.
5. Disable public access to secret stores.

**Outcome:** minimizes credential and data exposure.

### 10) Full observability and immutable audit
1. Enable Entra sign-in and audit logs.
2. Enable M365/SharePoint unified audit logs.
3. Export to SIEM (Sentinel/Splunk/ELK).
4. Alert on:
   - new consent grants,
   - credential/cert changes,
   - unusual volume/time/location patterns,
   - denied access attempts to non-allowed sites.
5. Retain logs per policy (e.g., 180–365+ days).

**Outcome:** rapid detection + forensic readiness.

### 11) Incident response runbook (pre-baked)
1. Define trigger: suspicious behavior/compromise indicators.
2. One-click containment actions:
   - disable service principal,
   - revoke/remove credentials,
   - remove site grant.
3. Test with quarterly tabletop exercises.
4. Track MTTD/MTTR and improve.

**Outcome:** fast containment with repeatable operations.

### 12) Governance and continuous assurance
1. Quarterly access review (is integration still required?).
2. Quarterly permission review (still only `Sites.Selected`?).
3. Cert rotation drill before real expiry.
4. Abuse/pentest scenarios for API access.
5. Keep auditable evidence (architecture, approvals, controls, tests).

**Outcome:** security remains strong after go-live.

---

## Hands-On Operator Runbook

### Step 1 — Isolate the directory ✅

- Dedicated site created: `ciso-isolated-site-for-automation` (Private group, 2 members).
- Dedicated document library created: `api-files-for-automation`.
- Directory isolated from other business content.

### Step 2 — Create dedicated Entra app ✅

- App registration: `sp-api-ciso-automation-prod`
- Single-tenant.
- Application (client) ID: `60c39b19-c445-4fe9-9898-a66c46a69877`
- Directory (tenant) ID: `894e5500-6b83-4c8e-b80d-2a46208b87bd`

### Step 3 — Configure certificate auth ✅

#### 3.1 Generate certificate pair (OpenSSL)
```bash
# private key (4096-bit RSA)
openssl genrsa -out sp-api-ciso-automation-prod.key 4096

# CSR
openssl req -new -key sp-api-ciso-automation-prod.key \
  -out sp-api-ciso-automation-prod.csr \
  -subj "/CN=sp-api-ciso-automation-prod"

# self-signed cert (365 days)
openssl x509 -req -days 365 \
  -in sp-api-ciso-automation-prod.csr \
  -signkey sp-api-ciso-automation-prod.key \
  -out sp-api-ciso-automation-prod.crt

# public cert for Entra upload (.cer DER format)
openssl x509 -in sp-api-ciso-automation-prod.crt -outform der \
  -out sp-api-ciso-automation-prod.cer

# PFX bundle for Key Vault import
openssl pkcs12 -export \
  -out sp-api-ciso-automation-prod.pfx \
  -inkey sp-api-ciso-automation-prod.key \
  -in sp-api-ciso-automation-prod.crt
```

#### 3.2 Upload certificate to app registration ✅
- Entra → App registration → `sp-api-ciso-automation-prod`
- `Certificates & secrets` → `Certificates` → `Upload certificate`
- Uploaded `*.cer`
- Thumbprint: `3BF7A08FEB025C43532C229F1B865FBFC17EC98A`
- Expiration: 2027-02-23

#### 3.3 Key Vault management ✅ (partial)
- PFX imported into Key Vault `vault-ciso-automati-prod` as certificate `sp-api-ciso-automation-prod-pfx`.
- Certificate status: **Enabled**, expiry 2027-02-23.

**Remaining (deferred):**
- [ ] Restrict Key Vault secret IAM to runtime identity only (`Key Vault Secrets User`, scoped to this secret).
- [ ] Remove broad inherited `Owner`/`Contributor` assignments where safe.
- [ ] Enable soft-delete + purge protection.
- [ ] Set up expiry alerting and rotation policy.
- [ ] Restrict Key Vault network access (private endpoint or selected networks).

#### 3.4 Troubleshooting notes
- If `Secrets` pane appears empty after PFX import, open the certificate and check `Secret Identifier (sid)`.
  If `sid` exists, the secret exists — this is a portal RBAC visibility issue.
- If portal shows intermittent IAM errors, retry after a few minutes (propagation delay).
- **No client secret was created** ✅

### Step 4 — Add Graph permission `Sites.Selected` ✅

- Entra app → API permissions → Microsoft Graph → Application → `Sites.Selected`
- Admin consent granted for tenant `Pitagone`.
- Also present (default): `User.Read` (Delegated) — can be removed for stricter least-privilege.

### Step 5 — Grant site-level access to app ✅

**Permission granted on 2026-02-23:**
- Role: `read`
- App: `sp-api-ciso-automation-prod` (`60c39b19-c445-4fe9-9898-a66c46a69877`)
- Site: `ciso-isolated-site-for-automation`
- Permission ID: `aTowaS50fG1zLnNwLmV4dHw2MGMzOWIxOS1jNDQ1LTRmZTktOTg5OC1hNjZjNDZhNjk4NzdAODk0ZTU1MDAtNmI4My00YzhlLWI4MGQtMmE0NjIwOGI4N2Jk`

#### Scripts used

**PowerShell script (recommended — works on Windows with PowerShell 7+):**

> Script: `scripts/grant-sharepoint-sites-selected.ps1`
>
> ```powershell
> pwsh -ExecutionPolicy Bypass -File .\scripts\grant-sharepoint-sites-selected.ps1
> pwsh -ExecutionPolicy Bypass -File .\scripts\grant-sharepoint-sites-selected.ps1 -Role write
> ```

**Bash script (Linux — requires `Sites.FullControl.All` delegated scope in token):**

> Script: `scripts/grant-sharepoint-sites-selected.sh`
>
> ```bash
> ./scripts/grant-sharepoint-sites-selected.sh
> # or skip login if already authenticated:
> AZ_SKIP_LOGIN=1 ./scripts/grant-sharepoint-sites-selected.sh
> ```

#### Known issues encountered during Step 5

| Issue | Cause | Fix |
|-------|-------|-----|
| `accessDenied` on POST `/sites/{id}/permissions` | Token missing `Sites.FullControl.All` scope | Use Graph PowerShell instead of `az` CLI |
| `AADSTS65002` when requesting scope via `az` | Tenant blocks Azure CLI first-party app from that scope | Switch to Microsoft.Graph PowerShell module |
| `DeviceCodeCredential: Object reference not set` | Known bug in Microsoft.Graph module on Windows PowerShell 5.1 and with WAM enabled | Use PowerShell 7+ (`pwsh`) with WAM disabled |
| PowerShell execution policy block | Scripts disabled on system | Run with `-ExecutionPolicy Bypass` |

### Step 6 — Operational hardening (deferred)

> Complete these controls before production use or during next security review.

#### 6.1 Conditional Access for workload identity
- [ ] Create CA policy targeting service principal `sp-api-ciso-automation-prod`.
- [ ] Restrict to expected network/IP ranges.
- [ ] Block unsupported/legacy auth paths.
- [ ] Start in report-only mode, then enforce after validation.

#### 6.2 Monitoring and alerting (SIEM)
- [ ] Enable Entra sign-in logs for service principals.
- [ ] Enable M365 Unified Audit Log.
- [ ] Enable SharePoint audit events.
- [ ] Export logs to SIEM (Sentinel/Splunk/ELK).
- [ ] Create alerts for:
  - New consent grants on the app.
  - Credential/certificate changes.
  - Unusual access volume, time, or source IP.
  - Access attempts to non-allowed sites.
  - App disabled/re-enabled events.
- [ ] Set log retention per compliance policy (180–365+ days).

#### 6.3 Incident response runbook
- [ ] Define compromise indicators / trigger criteria.
- [ ] Prepare one-click containment actions:
  - Disable service principal (Entra → Enterprise Apps → Properties → Enabled = No).
  - Revoke/remove certificate credentials.
  - Remove site permission grant:
    ```
    DELETE /sites/{siteId}/permissions/{permissionId}
    ```
  - Rotate certificate if compromised.
- [ ] Document escalation contacts and communication plan.
- [ ] Tabletop exercise quarterly.
- [ ] Track MTTD/MTTR metrics.

#### 6.4 Governance and continuous assurance
- [ ] Quarterly access review: confirm integration is still needed.
- [ ] Quarterly permission review: verify only `Sites.Selected` + single site grant.
- [ ] Certificate rotation drill before real expiry (current: 2027-02-23).
- [ ] Penetration test / red-team API abuse scenarios.
- [ ] Maintain auditable evidence: architecture decisions, approval records, test results.

#### 6.5 Cleanup recommendations
- [ ] Remove `User.Read` (Delegated) from API permissions if not needed.
- [ ] Review elevated access warning on Key Vault and remove unnecessary role assignments.
- [ ] Verify no other apps have access to the isolated site.

---

## Quick Compliance Checklist

- [x] Dedicated SharePoint site/library created
- [x] Directory isolated from other business content
- [x] Dedicated app registration per environment
- [x] Certificate auth enabled (no client secret)
- [x] PFX stored in Key Vault
- [ ] Key Vault secret access restricted to runtime identity only
- [x] Graph permission only `Sites.Selected`
- [x] App granted only target site with minimal role (read)
- [ ] Conditional Access for workload identity enforced
- [ ] API path allowlist + traversal protection in place
- [ ] Logging + SIEM alerts enabled
- [ ] Incident runbook tested
- [ ] Quarterly access/permission review scheduled

---

## TODOs (pre-production)

> Separate tracked items to address before moving to production.

### TODO-1: Replace personal user with dedicated runtime identity on Key Vault

- **What:** Currently, `abdelkrimb@pitagone.com` (personal user) is assigned Key Vault access. Replace with a dedicated runtime identity.
- **When:** When the runtime workload is defined (e.g., Azure Function, VM, container).
- **How:**
  1. Create or identify the runtime service principal / managed identity.
  2. Assign `Key Vault Secrets User` role on `vault-ciso-automati-prod`.
  3. Remove personal user's broad roles (`Key Vault Administrator`, `Certificates Officer`, `Secrets Officer`).
  4. Keep personal admin access via PIM/JIT only.
  5. Verify runtime identity can read the certificate secret.
  6. Verify personal user can no longer read secrets without JIT elevation.

### TODO-2: Restrict Key Vault network access

- **What:** Key Vault is currently set to "Allow public access from all networks". Acceptable for dev/testing, not for production.
- **When:** When runtime environment is known (IP/VNet/tunnel).
- **Options (pick one):**
  1. **IP firewall + cron (simple):** Add runtime IP, use cron to update if dynamic. Script example:
     ```bash
     CURRENT_IP="$(curl -s ifconfig.me)"
     az keyvault network-rule add --name vault-ciso-automati-prod --ip-address "${CURRENT_IP}/32"
     ```
  2. **Cloudflare Tunnel + Private Endpoint (production-grade):** Route traffic through Cloudflare Tunnel to Azure Private Endpoint. No public IP exposure at all.
  3. **VNet integration:** If runtime is in Azure, use VNet service endpoint or private endpoint directly.
- **Note:** Always keep ✅ "Allow trusted Microsoft services to bypass this firewall" enabled.

---

## Notes

- If true folder-level hard isolation is mandatory, use **information architecture isolation** (dedicated site) rather than relying on broad tenant permissions.
- Keep this integration independent from other automations to prevent privilege creep.
- Never commit keys/certs (`.key`, `.pfx`, `.csr`, `.crt`, `.cer`) to source control.
- Certificate expires **2027-02-23** — set a reminder to rotate before that date.
- The `User.Read` delegated permission is a default that can be safely removed for daemon/app-only scenarios.
