import type { AISentinelConfig, AuditEntry, PluginLogger, ScanResult } from "../types.js";
import { scan } from "../scanner/detector.js";
import { resolveAgentConfig } from "../config.js";
import { trackAgent } from "../agent-tracker.js";
import type { APIReporter } from "../api-reporter.js";
import * as log from "../logger.js";

// =============================================================================
// message_received hook
//
// ACTUAL SDK BEHAVIOR: This hook is void/parallel — it cannot block or modify
// the inbound message. We use it for monitoring and threat logging only.
//
// In enforce mode, detected threats are recorded in a shared registry so that
// the before_agent_start hook can inject blocking context.
//
// Reporting modes:
//   telemetry:  Local scan runs → report results (no raw text unless opted in)
//   cloud-scan + monitor: Skip local scan, send raw text to API
//   cloud-scan + enforce: Local scan for blocking + async API scan for deeper analysis
// =============================================================================

export interface InboundMessagePayload {
  message: string;
  senderId?: string;
  channel?: string;
  sessionKey: string;
  agentId?: string;
  [key: string]: unknown;
}

/** In-memory registry of recent threats for cross-hook coordination */
const recentThreats = new Map<string, ScanResult>();

export function getRecentThreat(sessionKey: string): ScanResult | undefined {
  return recentThreats.get(sessionKey);
}

export function clearRecentThreat(sessionKey: string): void {
  recentThreats.delete(sessionKey);
}

export function createMessageReceivedHook(
  config: AISentinelConfig,
  logger: PluginLogger,
  reporter: APIReporter | null = null,
) {
  return function messageReceived(payload: InboundMessagePayload): void {
    const { message, sessionKey, senderId, channel, agentId } = payload;

    trackAgent(agentId);
    const effectiveConfig = resolveAgentConfig(config, agentId);
    if (!effectiveConfig) {
      log.debug(`Skipping excluded agent: ${agentId}`);
      return;
    }

    // Skip allowlisted sessions
    if (effectiveConfig.allowlist.includes(sessionKey)) {
      log.debug(`Skipping allowlisted session: ${sessionKey}`);
      return;
    }

    // Skip empty messages
    if (!message || message.trim().length === 0) {
      return;
    }

    const reportCtx = {
      sessionKey,
      channel,
      senderId,
      agentId,
      location: "message" as const,
    };

    // Cloud-scan + monitor: skip local scan, send raw text to API
    if (effectiveConfig.reportMode === "cloud-scan" && effectiveConfig.mode === "monitor") {
      reporter?.report("message_scan", message, null, reportCtx);
      log.debug(`Cloud-scan dispatched for message [session=${sessionKey}]`);
      return;
    }

    // All other modes: run local scan
    const result = scan(message, effectiveConfig, { location: "message" });

    // Report to API (telemetry sends results, cloud-scan+enforce sends raw text async)
    if (reporter) {
      reporter.report("message_scan", message, result, reportCtx);
    }

    // Always audit non-clean results
    if (!result.safe) {
      const entry: AuditEntry = {
        timestamp: new Date().toISOString(),
        eventType: "message_scan",
        sessionKey,
        channel,
        senderId,
        scanResult: result,
        ...(effectiveConfig.logLevel === "debug" ? { rawInput: message.slice(0, 500) } : {}),
      };
      log.audit(entry).catch(() => {});

      log.warn(
        `${result.summary} [session=${sessionKey}, sender=${senderId ?? "?"}]`,
      );

      // In enforce mode, record the threat for the before_agent_start hook
      if (result.action === "block") {
        recentThreats.set(sessionKey, result);
        log.error(
          `THREAT RECORDED for session ${sessionKey}: ${result.summary}`,
        );

        const blockEntry: AuditEntry = {
          timestamp: new Date().toISOString(),
          eventType: "block",
          sessionKey,
          channel,
          senderId,
          scanResult: result,
        };
        log.audit(blockEntry).catch(() => {});
      }
    } else {
      log.debug(
        `Clean message from ${senderId ?? "?"} [${formatScanTime(result.scanTimeMs)}]`,
      );
    }
  };
}

function formatScanTime(ms: number): string {
  return ms < 1 ? "<1ms" : `${ms.toFixed(1)}ms`;
}
