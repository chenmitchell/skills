import type { AISentinelConfig, AuditEntry, PluginLogger } from "../types.js";
import { scan, extractText } from "../scanner/detector.js";
import { resolveAgentConfig } from "../config.js";
import { trackAgent } from "../agent-tracker.js";
import type { APIReporter } from "../api-reporter.js";
import * as log from "../logger.js";

// =============================================================================
// before_tool_call hook
//
// Layer 3: Intercepts tool parameters before execution.
// Scans for data exfiltration patterns (URLs to attacker-controlled hosts,
// shell injection in exec params) and blocks when threats detected.
//
// Returns { block: true, blockReason } to prevent tool execution.
//
// Reporting modes:
//   telemetry:  Local scan runs → report results
//   cloud-scan + monitor: Skip local scan, send raw text to API
//   cloud-scan + enforce: Local scan for blocking + async API scan
// =============================================================================

export interface ToolCallPayload {
  toolName: string;
  parameters: Record<string, unknown>;
  sessionKey?: string;
  agentId?: string;
  [key: string]: unknown;
}

export interface BeforeToolCallReturn {
  block?: boolean;
  blockReason?: string;
}

export function createBeforeToolCallHook(
  config: AISentinelConfig,
  logger: PluginLogger,
  reporter: APIReporter | null = null,
) {
  return function beforeToolCall(
    payload: ToolCallPayload,
  ): BeforeToolCallReturn | undefined {
    const { toolName, parameters, sessionKey = "unknown", agentId } = payload;

    trackAgent(agentId);
    const effectiveConfig = resolveAgentConfig(config, agentId);
    if (!effectiveConfig) {
      log.debug(`Skipping excluded agent: ${agentId}`);
      return undefined;
    }

    // Extract text from all parameter values
    const text = extractText(parameters);

    if (!text || text.trim().length === 0) {
      return undefined;
    }

    const reportCtx = {
      sessionKey,
      toolName,
      agentId,
      location: "tool_params" as const,
    };

    // Cloud-scan + monitor: skip local scan, send raw text to API
    if (effectiveConfig.reportMode === "cloud-scan" && effectiveConfig.mode === "monitor") {
      reporter?.report("tool_call_scan", text, null, reportCtx);
      log.debug(`Cloud-scan dispatched for tool call ${toolName} [session=${sessionKey}]`);
      return undefined;
    }

    const scanResult = scan(text, effectiveConfig, { location: "tool_params" });

    // Report to API
    if (reporter) {
      reporter.report("tool_call_scan", text, scanResult, reportCtx);
    }

    if (!scanResult.safe) {
      const entry: AuditEntry = {
        timestamp: new Date().toISOString(),
        eventType: "tool_call_scan",
        sessionKey,
        toolName,
        scanResult,
        ...(effectiveConfig.logLevel === "debug" ? { rawInput: text.slice(0, 500) } : {}),
      };
      log.audit(entry).catch(() => {});

      log.warn(
        `Tool param threat in ${toolName}: ${scanResult.summary} [session=${sessionKey}]`,
      );

      if (scanResult.action === "block") {
        log.error(
          `BLOCKING tool call ${toolName} [session=${sessionKey}]: ${scanResult.summary}`,
        );

        return {
          block: true,
          blockReason: [
            `[AI Sentinel] Blocked tool "${toolName}" due to detected security threats in parameters.`,
            `Categories: ${[...new Set(scanResult.threats.map((t) => t.category))].join(", ")}`,
            `Confidence: ${(scanResult.highestConfidence * 100).toFixed(0)}%`,
          ].join(" "),
        };
      }
    } else {
      log.debug(`Clean tool params for ${toolName} [${scanResult.scanTimeMs.toFixed(1)}ms]`);
    }

    return undefined;
  };
}
