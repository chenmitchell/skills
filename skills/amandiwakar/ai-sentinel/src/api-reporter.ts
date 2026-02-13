import { createHash, randomUUID } from "node:crypto";
import { homedir } from "node:os";
import type { AISentinelConfig, ScanResult } from "./types.js";
import * as log from "./logger.js";

// =============================================================================
// API Reporter — Dispatches scan results to AI Sentinel API
//
// Two modes:
//   telemetry   — batch local scan results, flush periodically to POST /v1/telemetry
//   cloud-scan  — fire-and-forget raw text to API scan endpoints for full rule engine
//
// Privacy:
//   - Session keys are SHA-256 hashed before sending (telemetry mode)
//   - Raw input text is NEVER sent unless includeRawInput = true
//   - Matched text preview truncated to 50 chars when raw input opted in
//
// Resilience:
//   - Exponential backoff on flush failures (5s → 10s → 20s → … → 5min cap)
//   - Events re-queued on failed flush for retry
//   - Self-disables on 401/403 (bad API key)
//   - 5-second timeout per request via AbortController
//   - Never blocks hooks (fire-and-forget)
// =============================================================================

const PLUGIN_VERSION = "0.1.0";
const REQUEST_TIMEOUT_MS = 5_000;
const MAX_RETRY_DELAY_MS = 5 * 60 * 1000;
const INITIAL_RETRY_DELAY_MS = 5_000;

export interface TelemetryEvent {
  eventId: string;
  timestamp: string;
  instanceId: string;
  pluginVersion: string;
  eventType: string;
  agentId?: string;
  sessionKey: string;
  channel?: string;
  threats: Array<{
    category: string;
    pattern: string;
    confidence: number;
    location: string;
    matchedPreview?: string;
  }>;
  highestConfidence: number;
  action: string;
  scanTimeMs: number;
  rawInput?: string;
}

export interface ReportContext {
  sessionKey: string;
  channel?: string;
  senderId?: string;
  toolName?: string;
  agentId?: string;
  location: string;
}

export class APIReporter {
  private config: AISentinelConfig;
  private instanceId: string;
  private batch: TelemetryEvent[] = [];
  private flushTimer: ReturnType<typeof setInterval> | null = null;
  private disabled = false;
  private consecutiveFailures = 0;
  private retryDelayMs = INITIAL_RETRY_DELAY_MS;

  constructor(config: AISentinelConfig) {
    this.config = config;
    this.instanceId = generateInstanceId();

    if (config.reportMode === "telemetry") {
      this.flushTimer = setInterval(() => {
        this.flush().catch(() => {});
      }, config.flushIntervalMs);
      // Allow process to exit even if timer is pending
      if (this.flushTimer.unref) {
        this.flushTimer.unref();
      }
    }
  }

  /**
   * Report a scan event. Dispatches to telemetry or cloud-scan based on config.
   */
  report(
    eventType: string,
    rawText: string,
    scanResult: ScanResult | null,
    ctx: ReportContext,
  ): void {
    if (this.disabled) return;

    if (this.config.reportMode === "telemetry") {
      this.reportTelemetry(eventType, rawText, scanResult, ctx);
    } else if (this.config.reportMode === "cloud-scan") {
      this.reportCloudScan(eventType, rawText, ctx);
    }
  }

  /**
   * Telemetry mode: queue event for batch flush.
   */
  private reportTelemetry(
    eventType: string,
    rawText: string,
    scanResult: ScanResult | null,
    ctx: ReportContext,
  ): void {
    // If threats-only, skip clean scans
    if (
      this.config.reportFilter === "threats-only" &&
      scanResult &&
      scanResult.safe
    ) {
      return;
    }

    const includeRaw = this.config.includeRawInput;

    const event: TelemetryEvent = {
      eventId: randomUUID(),
      timestamp: new Date().toISOString(),
      instanceId: this.instanceId,
      pluginVersion: PLUGIN_VERSION,
      eventType,
      agentId: ctx.agentId,
      // Hash session key for privacy unless raw input mode
      sessionKey: includeRaw ? ctx.sessionKey : hashValue(ctx.sessionKey),
      channel: ctx.channel,
      threats: scanResult
        ? scanResult.threats.map((t) => ({
            category: t.category,
            pattern: t.patternId,
            confidence: t.confidence,
            location: ctx.location,
            matchedPreview: includeRaw ? t.matchedText.slice(0, 50) : undefined,
          }))
        : [],
      highestConfidence: scanResult?.highestConfidence ?? 0,
      action: scanResult?.action ?? "allow",
      scanTimeMs: scanResult?.scanTimeMs ?? 0,
    };

    if (includeRaw && rawText) {
      event.rawInput = rawText;
    }

    this.batch.push(event);

    if (this.batch.length >= this.config.flushBatchSize) {
      this.flush().catch(() => {});
    }
  }

  /**
   * Cloud-scan mode: send raw text to API scan endpoints.
   */
  private reportCloudScan(
    eventType: string,
    rawText: string,
    ctx: ReportContext,
  ): void {
    if (!rawText || rawText.trim().length === 0) return;

    let endpoint: string;
    let body: Record<string, unknown>;

    const agentId = ctx.agentId || this.config.agentId;

    if (eventType === "tool_result_scan") {
      endpoint = "/v1/scan/tool-result";
      body = {
        text: rawText,
        tool_name: ctx.toolName ?? "unknown",
        agent_id: agentId,
        session_id: ctx.sessionKey,
      };
    } else {
      // message_scan, tool_call_scan → input endpoint
      endpoint = "/v1/scan/input";
      body = {
        text: rawText,
        agent_id: agentId,
        session_id: ctx.sessionKey,
        user_id: ctx.senderId,
      };
    }

    this.sendRequest(endpoint, body, { "X-API-Key": this.config.apiKey });
  }

  /**
   * Flush batched telemetry events to API.
   */
  async flush(): Promise<void> {
    if (this.batch.length === 0 || this.disabled) return;

    const events = this.batch.splice(0);
    const batchId = randomUUID();

    const payload = {
      batchId,
      instanceId: this.instanceId,
      pluginVersion: PLUGIN_VERSION,
      eventCount: events.length,
      sentAt: new Date().toISOString(),
      events,
    };

    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.config.apiKey}`,
      "X-Sentinel-Instance": this.instanceId,
      "X-Sentinel-Version": PLUGIN_VERSION,
    };

    const ok = await this.sendRequest("/v1/telemetry", payload, headers);
    if (ok) {
      // Reset backoff on success
      this.consecutiveFailures = 0;
      this.retryDelayMs = INITIAL_RETRY_DELAY_MS;
      log.info(`Telemetry batch sent: ${events.length} accepted`);
    } else if (!this.disabled) {
      // Re-queue events for retry (put back at front)
      this.batch.unshift(...events);
      this.consecutiveFailures++;
      this.retryDelayMs = Math.min(
        MAX_RETRY_DELAY_MS,
        INITIAL_RETRY_DELAY_MS * Math.pow(2, this.consecutiveFailures - 1),
      );
      log.warn(
        `Telemetry flush failed (attempt ${this.consecutiveFailures}, ` +
          `retry in ${this.retryDelayMs / 1000}s)`,
      );
    }
  }

  /**
   * Fire-and-forget HTTP request with timeout and self-disable on auth errors.
   */
  private async sendRequest(
    path: string,
    body: Record<string, unknown>,
    extraHeaders: Record<string, string>,
  ): Promise<boolean> {
    const url = `${this.config.apiUrl.replace(/\/$/, "")}${path}`;

    try {
      const controller = new AbortController();
      const timeout = setTimeout(
        () => controller.abort(),
        REQUEST_TIMEOUT_MS,
      );

      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...extraHeaders,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (res.status === 401 || res.status === 403) {
        log.warn(
          `API reporting disabled: ${res.status} from ${path}. Check API key.`,
        );
        this.disabled = true;
        return false;
      }

      if (!res.ok) {
        log.warn(`API reporting error: ${res.status} from ${path}`);
        return false;
      }

      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      log.warn(`API reporting failed for ${path}: ${msg}`);
      return false;
    }
  }

  /**
   * Stop the flush timer and send any remaining events.
   */
  async shutdown(): Promise<void> {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    await this.flush();
  }
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Generate a stable instance ID from machine-level identifiers.
 * Uses multiple factors so the dashboard can group events by OpenClaw instance
 * without requiring manual configuration.
 */
function generateInstanceId(): string {
  const factors = [
    homedir(),
    process.env.USER ?? process.env.USERNAME ?? "",
    process.env.HOSTNAME ?? "",
    process.platform,
  ].join("|");

  return createHash("sha256").update(factors).digest("hex").slice(0, 16);
}

/** SHA-256 hash for privacy-sensitive values */
function hashValue(value: string): string {
  return createHash("sha256").update(value).digest("hex").slice(0, 12);
}
