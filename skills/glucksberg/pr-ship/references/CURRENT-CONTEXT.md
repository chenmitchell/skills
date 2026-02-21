# Current Context

<!--
  Version-specific gotchas, behavioral changes, and active risk areas.

  Keep this file updated when upgrading OpenClaw versions.
  You can update it manually by reading the top 2 version sections of CHANGELOG.md,
  or automate it via a cron/sync script that detects changelog changes.

  Retention: Keep the 4 most recent version sections. Drop older ones to control file size.
  The "Foundational Gotchas" section is permanent and must be manually maintained.

  Last updated: 2026-02-21
  Source: CHANGELOG.md versions 2026.2.20 (Unreleased) through 2026.2.17
-->

---

## Active Version

- Current: 2026.2.20 (Unreleased)
- Previous stable: 2026.2.19

---

## Foundational Gotchas (Folk Knowledge)

These are architectural traps that have no CHANGELOG entry. They exist since early codebase design and must be manually maintained.

1. **`loadConfig()` is synchronous with caching** -- First call reads disk (`fs.readFileSync`). Never call in hot paths. Use `clearConfigCache()` to invalidate.
2. **Route resolution uses `WeakMap` cache on config object** -- Spreading/cloning config causes cache miss. Pass config by reference.
3. **Session keys are hierarchical** -- Format: `agent:<id>:<channel>:<kind>:<peerId>[:thread:<threadId>]`. Functions like `isSubagentSessionKey()` depend on exact format.
4. **`agents/` <-> `auto-reply/` is bidirectional by design** -- Not a circular dependency bug. `agents/` provides runtime, `auto-reply/` orchestrates it.
5. **`pi-embedded-subscribe.ts` is a streaming state machine** -- Adding/removing events can break tool call parsing, block chunking, or reasoning block extraction.
6. **`VerboseLevel` enum values are persisted in sessions** -- Changing enum values in `auto-reply/thinking.ts` breaks session persistence.
7. **`channels/dock.ts` returns lightweight metadata** -- Must be updated when channel capabilities change, even though it doesn't import heavy channel code.
8. **`infra/outbound/deliver.ts` is dual-use** -- Used by both cron delivery AND message tool sends. Test both paths.
9. **File locking is required for stores** -- `sessions/` and `cron/` use file locking. Removing lock wrappers causes race conditions and data corruption.
10. **JSON5 vs JSON parsers** -- Config files are JSON5 (comments, trailing commas). Session files, cron store, auth profiles are strict JSON. Don't mix parsers.
11. **`config.patch` nesting trap** -- Patching `{"telegram":{"streamMode":"off"}}` writes to an ignored top-level key. Correct: `{"channels":{"telegram":{"streamMode":"off"}}}`. Always verify full nested structure.
12. **Telegram HTML formatting** -- `telegram/format.ts` converts Markdown to Telegram's limited HTML subset. Broken HTML fails silently.
13. **Discord 2000 char limit** -- `discord/chunk.ts` enforces limits with fence-aware splitting. Don't bypass the chunker.
14. **Signal styled text uses byte positions** -- Not character positions. Multi-byte chars shift ranges.
15. **WhatsApp target normalization** -- Converts between E.164, JID (`@s.whatsapp.net`), and display formats. Wrong format = silent failure.

---

## Recent Behavioral Changes (v2026.2.19 - v2026.2.20)

### From v2026.2.20 (Unreleased) -- 65 entries

- Agents: Preserve pi-ai default OAuth beta headers when `context1m` injects `anthropic-beta`.
- Telegram: Fix draft stream cleanup ordering -- `finally` block must run after fallback delivery logic, not before (#19001).
- Telegram: Fix `disableBlockStreaming` evaluation order -- ternary producing `undefined` instead of `true` when `streamMode === "off"`.

### From v2026.2.19 -- 80 entries

- **Gateway auth defaults to token mode.** `gateway.auth.mode` is no longer implicitly open. Auto-generated `gateway.auth.token` persisted on first start.
- **`hooks.token` must differ from `gateway.auth.token`** -- startup validation rejects identical values.
- **YAML 1.2 core schema for frontmatter** -- `on`/`off`/`yes`/`no` are now strings, not booleans.
- **Cron webhook delivery is SSRF-guarded** -- private addresses, metadata endpoints blocked.
- **SSRF bypass via IPv6 transition addresses blocked** -- NAT64, 6to4, Teredo, ISATAP.
- **Browser relay requires gateway-token auth** on `/extension` and `/cdp`.
- **`tools.exec.safeBins` validates trusted bin directories** -- trojan binaries in late PATH rejected.
- **Canvas/A2UI uses node-scoped session capability URLs** -- shared-IP fallback auth removed.
- **Control-plane RPCs rate-limited** -- `config.apply`, `config.patch`, `update.run` at 3/min per device+IP.
- **Plaintext `ws://` to non-loopback hosts blocked** -- only `wss://` for remote WebSocket.
- **Discord moderation enforces guild permissions** on trusted sender.
- **Heartbeat skips when HEARTBEAT.md missing/empty** -- cron-event fallback preserved.
- **Cron/heartbeat Telegram topic delivery fixed** -- explicit `<chatId>:topic:<threadId>` targets work correctly.
- **macOS LaunchAgent SQLite fix** -- `TMPDIR` forwarded into installed service environments.

---

## Recent Gotchas (v2026.2.17 - v2026.2.18)

### From v2026.2.18

- **Pass API tokens explicitly in every call** -- missing token causes silent auth failure.
- **Use logging abstraction, not `console.*`** -- raw console bypasses user-controlled verbosity.
- **Identity checks must compare exact values** -- `(a && b)` is not `(a === b)`.
- **Don't mix ID namespaces for message provenance** -- file IDs are not message timestamps.
- **Classify shell builtins by token list** -- `resolveExecutablePath()` finds PATH-shadowed binaries.
- **Close resource pools on every call** -- unclosed `ProxyAgent` pools leak.
- **Validate URLs before constructing connection objects** -- invalid proxy URL crashes execution.
- **Duplicate inverse conditions = dead code** -- Block A skips non-gateway, Block B skips gateway = nothing runs.
- **Run `pnpm protocol:gen:swift` after protocol schema changes.**

### From v2026.2.17

- **Config include confinement is strict** -- `$include` confined to top-level config directory.
- **Cron top-of-hour defaults are staggered** -- `schedule.staggerMs` persisted. Use `--exact` for clock boundaries.
- **`sessions_spawn` is push-first** -- polling can trip loop protections.
- **Tool-loop detection hard-blocks no-progress loops** -- use progress checks/backoff/exit criteria.
- **Read truncation markers are actionable** -- recover with smaller targeted reads, not full-file retries.
- **Z.AI tool streaming defaults ON** -- explicitly set `params.tool_stream: false` if needed.
- **Anthropic 1M context is explicit opt-in** -- `params.context1m: true` controls the beta header.
- **`read` tool auto-pages using model contextWindow** -- behavior change from bounded single-call read.
- **exec preflight guard for env var injection** -- scripts with shell env vars blocked.

---

## Recently Active High-Risk Areas

Modules appearing frequently in v2026.2.19 and v2026.2.20:

| Module | Recent Activity | Risk |
| --- | --- | --- |
| Security | SSRF hardening, gateway auth, exec guards, browser relay auth | CRITICAL |
| Gateway | Auth mode defaults, token validation, rate limiting, startup validation | HIGH |
| Agents | Read auto-paging, exec preflight, tool loop detection, subagent depth | CRITICAL |
| Telegram | Draft stream cleanup, block streaming evaluation, topic delivery | MEDIUM |
| Cron | Webhook SSRF guard, heartbeat skip logic, stagger persistence | LOW (module) / HIGH (impact) |
| Config | Include confinement, YAML 1.2 parsing, patch nesting | CRITICAL |

---

## Pre-PR Checklist Additions (Version-Specific)

These supplement the stable checklist in STABLE-PRINCIPLES.md:

```
[] If touching gateway auth: verify gateway.auth.mode explicitly. Ensure hooks.token != gateway.auth.token.
[] If touching security: run `openclaw security audit` and triage all findings first.
[] If using YAML frontmatter: use explicit true/false, not on/off/yes/no.
[] If touching cron webhooks: verify targets are publicly reachable HTTPS.
[] If installing plugins: use --pin flag. Record name, version, spec, integrity.
[] If touching canvas/A2UI: use scoped session capability URLs, not shared-IP auth.
[] If touching protocol schemas: run pnpm protocol:gen:swift && pnpm protocol:check.
[] If touching config loading: test negative path for out-of-root $include and symlink escape.
[] If touching cron schedules: verify both expression and persisted schedule.staggerMs.
```
