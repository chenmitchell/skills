export type ThreatCategory = "prompt_injection" | "jailbreak" | "instruction_override" | "data_exfiltration" | "social_engineering" | "tool_abuse" | "indirect_injection";
export type ScanLocation = "message" | "tool_result" | "tool_params" | "system";
export type ScanAction = "allow" | "warn" | "block";
export interface AgentOverride {
    agentId: string;
    mode?: "monitor" | "enforce";
    threatThreshold?: number;
}
export interface ThreatMatch {
    patternId: string;
    category: ThreatCategory;
    confidence: number;
    description: string;
    matchedText: string;
}
export interface ScanResult {
    safe: boolean;
    action: ScanAction;
    threats: ThreatMatch[];
    highestConfidence: number;
    summary: string;
    scanTimeMs: number;
}
export interface AISentinelConfig {
    mode: "monitor" | "enforce";
    logLevel: "debug" | "info" | "warn" | "error";
    threatThreshold: number;
    allowlist: string[];
    apiUrl: string;
    apiKey: string;
    reportMode: "telemetry" | "cloud-scan" | "none";
    reportFilter: "all" | "threats-only";
    agentId: string;
    includeRawInput: boolean;
    flushIntervalMs: number;
    flushBatchSize: number;
    excludeAgents: string[];
    agentOverrides: AgentOverride[];
}
export type LogLevel = AISentinelConfig["logLevel"];
export interface AuditEntry {
    timestamp: string;
    eventType: string;
    sessionKey?: string;
    channel?: string;
    senderId?: string;
    toolName?: string;
    scanResult?: ScanResult;
    rawInput?: string;
}
export interface PluginLogger {
    debug(msg: string): void;
    info(msg: string): void;
    warn(msg: string): void;
    error(msg: string): void;
}
export interface AgentMessage {
    role: string;
    content: string;
    [key: string]: unknown;
}
export interface PluginTool {
    name: string;
    description: string;
    parameters: Record<string, {
        type: string;
        description: string;
        required?: boolean;
    }>;
    execute(params: Record<string, unknown>): Promise<string> | string;
}
export interface PluginAPI {
    pluginConfig: Record<string, unknown>;
    logger: PluginLogger;
    on(event: string, handler: (event: any, ctx: any) => unknown, options?: {
        priority?: number;
    }): void;
    registerTool(tool: PluginTool): void;
}
export interface OpenClawPlugin {
    id: string;
    name: string;
    register(api: PluginAPI): void;
}
//# sourceMappingURL=types.d.ts.map