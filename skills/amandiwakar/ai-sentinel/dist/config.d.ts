import { z } from "zod";
import type { AISentinelConfig } from "./types.js";
export declare const AgentOverrideSchema: z.ZodObject<{
    agentId: z.ZodString;
    mode: z.ZodOptional<z.ZodEnum<["monitor", "enforce"]>>;
    threatThreshold: z.ZodOptional<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    agentId: string;
    mode?: "monitor" | "enforce" | undefined;
    threatThreshold?: number | undefined;
}, {
    agentId: string;
    mode?: "monitor" | "enforce" | undefined;
    threatThreshold?: number | undefined;
}>;
export declare const AISentinelConfigSchema: z.ZodObject<{
    mode: z.ZodDefault<z.ZodEnum<["monitor", "enforce"]>>;
    logLevel: z.ZodDefault<z.ZodEnum<["debug", "info", "warn", "error"]>>;
    threatThreshold: z.ZodDefault<z.ZodNumber>;
    allowlist: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    apiUrl: z.ZodDefault<z.ZodString>;
    apiKey: z.ZodDefault<z.ZodString>;
    reportMode: z.ZodDefault<z.ZodEnum<["telemetry", "cloud-scan", "none"]>>;
    reportFilter: z.ZodDefault<z.ZodEnum<["all", "threats-only"]>>;
    agentId: z.ZodDefault<z.ZodString>;
    includeRawInput: z.ZodDefault<z.ZodBoolean>;
    flushIntervalMs: z.ZodDefault<z.ZodNumber>;
    flushBatchSize: z.ZodDefault<z.ZodNumber>;
    excludeAgents: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    agentOverrides: z.ZodDefault<z.ZodArray<z.ZodObject<{
        agentId: z.ZodString;
        mode: z.ZodOptional<z.ZodEnum<["monitor", "enforce"]>>;
        threatThreshold: z.ZodOptional<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        agentId: string;
        mode?: "monitor" | "enforce" | undefined;
        threatThreshold?: number | undefined;
    }, {
        agentId: string;
        mode?: "monitor" | "enforce" | undefined;
        threatThreshold?: number | undefined;
    }>, "many">>;
}, "strip", z.ZodTypeAny, {
    logLevel: "warn" | "debug" | "info" | "error";
    agentId: string;
    mode: "monitor" | "enforce";
    threatThreshold: number;
    allowlist: string[];
    apiUrl: string;
    apiKey: string;
    reportMode: "telemetry" | "cloud-scan" | "none";
    reportFilter: "all" | "threats-only";
    includeRawInput: boolean;
    flushIntervalMs: number;
    flushBatchSize: number;
    excludeAgents: string[];
    agentOverrides: {
        agentId: string;
        mode?: "monitor" | "enforce" | undefined;
        threatThreshold?: number | undefined;
    }[];
}, {
    logLevel?: "warn" | "debug" | "info" | "error" | undefined;
    agentId?: string | undefined;
    mode?: "monitor" | "enforce" | undefined;
    threatThreshold?: number | undefined;
    allowlist?: string[] | undefined;
    apiUrl?: string | undefined;
    apiKey?: string | undefined;
    reportMode?: "telemetry" | "cloud-scan" | "none" | undefined;
    reportFilter?: "all" | "threats-only" | undefined;
    includeRawInput?: boolean | undefined;
    flushIntervalMs?: number | undefined;
    flushBatchSize?: number | undefined;
    excludeAgents?: string[] | undefined;
    agentOverrides?: {
        agentId: string;
        mode?: "monitor" | "enforce" | undefined;
        threatThreshold?: number | undefined;
    }[] | undefined;
}>;
export declare function parseConfig(raw: Record<string, unknown>): AISentinelConfig;
/**
 * Resolve effective config for a specific agent.
 *
 * Returns null if the agent is excluded (caller should skip scanning).
 * Returns config with per-agent overrides merged if an override entry exists.
 * Returns the base config unchanged otherwise.
 */
export declare function resolveAgentConfig(config: AISentinelConfig, agentId: string | undefined): AISentinelConfig | null;
//# sourceMappingURL=config.d.ts.map