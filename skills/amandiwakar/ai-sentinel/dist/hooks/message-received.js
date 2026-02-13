import { scan } from "../scanner/detector.js";
import { resolveAgentConfig } from "../config.js";
import { trackAgent } from "../agent-tracker.js";
import * as log from "../logger.js";
/** In-memory registry of recent threats for cross-hook coordination */
const recentThreats = new Map();
export function getRecentThreat(sessionKey) {
    return recentThreats.get(sessionKey);
}
export function clearRecentThreat(sessionKey) {
    recentThreats.delete(sessionKey);
}
export function createMessageReceivedHook(config, logger, reporter = null) {
    return function messageReceived(payload) {
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
            location: "message",
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
            const entry = {
                timestamp: new Date().toISOString(),
                eventType: "message_scan",
                sessionKey,
                channel,
                senderId,
                scanResult: result,
                ...(effectiveConfig.logLevel === "debug" ? { rawInput: message.slice(0, 500) } : {}),
            };
            log.audit(entry).catch(() => { });
            log.warn(`${result.summary} [session=${sessionKey}, sender=${senderId ?? "?"}]`);
            // In enforce mode, record the threat for the before_agent_start hook
            if (result.action === "block") {
                recentThreats.set(sessionKey, result);
                log.error(`THREAT RECORDED for session ${sessionKey}: ${result.summary}`);
                const blockEntry = {
                    timestamp: new Date().toISOString(),
                    eventType: "block",
                    sessionKey,
                    channel,
                    senderId,
                    scanResult: result,
                };
                log.audit(blockEntry).catch(() => { });
            }
        }
        else {
            log.debug(`Clean message from ${senderId ?? "?"} [${formatScanTime(result.scanTimeMs)}]`);
        }
    };
}
function formatScanTime(ms) {
    return ms < 1 ? "<1ms" : `${ms.toFixed(1)}ms`;
}
//# sourceMappingURL=message-received.js.map