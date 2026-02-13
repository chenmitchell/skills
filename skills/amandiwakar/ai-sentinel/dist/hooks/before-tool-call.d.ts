import type { AISentinelConfig, PluginLogger } from "../types.js";
import type { APIReporter } from "../api-reporter.js";
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
export declare function createBeforeToolCallHook(config: AISentinelConfig, logger: PluginLogger, reporter?: APIReporter | null): (payload: ToolCallPayload) => BeforeToolCallReturn | undefined;
//# sourceMappingURL=before-tool-call.d.ts.map