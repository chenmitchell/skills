import type { AISentinelConfig, AgentMessage, PluginLogger } from "../types.js";
import type { APIReporter } from "../api-reporter.js";
export interface ToolResultPayload {
    toolName: string;
    result: unknown;
    sessionKey?: string;
    agentId?: string;
    [key: string]: unknown;
}
export interface ToolResultHookReturn {
    message?: AgentMessage;
}
export declare function createToolResultPersistHook(config: AISentinelConfig, logger: PluginLogger, reporter?: APIReporter | null): (payload: ToolResultPayload) => ToolResultHookReturn | undefined;
//# sourceMappingURL=tool-result-persist.d.ts.map