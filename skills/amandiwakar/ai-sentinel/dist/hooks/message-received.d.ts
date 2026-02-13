import type { AISentinelConfig, PluginLogger, ScanResult } from "../types.js";
import type { APIReporter } from "../api-reporter.js";
export interface InboundMessagePayload {
    message: string;
    senderId?: string;
    channel?: string;
    sessionKey: string;
    agentId?: string;
    [key: string]: unknown;
}
export declare function getRecentThreat(sessionKey: string): ScanResult | undefined;
export declare function clearRecentThreat(sessionKey: string): void;
export declare function createMessageReceivedHook(config: AISentinelConfig, logger: PluginLogger, reporter?: APIReporter | null): (payload: InboundMessagePayload) => void;
//# sourceMappingURL=message-received.d.ts.map