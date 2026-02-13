import { z } from "zod";
import type { AISentinelConfig } from "./types.js";

export const AgentOverrideSchema = z.object({
  agentId: z.string(),
  mode: z.enum(["monitor", "enforce"]).optional(),
  threatThreshold: z.number().min(0).max(1).optional(),
});

export const AISentinelConfigSchema = z.object({
  mode: z.enum(["monitor", "enforce"]).default("monitor"),
  logLevel: z.enum(["debug", "info", "warn", "error"]).default("info"),
  threatThreshold: z.number().min(0).max(1).default(0.7),
  allowlist: z.array(z.string()).default([]),
  apiUrl: z.string().default("https://api.zetro.ai"),
  apiKey: z.string().default(""),
  reportMode: z.enum(["telemetry", "cloud-scan", "none"]).default("telemetry"),
  reportFilter: z.enum(["all", "threats-only"]).default("all"),
  agentId: z.string().default("openclaw-agent"),
  includeRawInput: z.boolean().default(false),
  flushIntervalMs: z.number().min(1000).default(10000),
  flushBatchSize: z.number().min(1).max(500).default(25),
  excludeAgents: z.array(z.string()).default([]),
  agentOverrides: z.array(AgentOverrideSchema).default([]),
});

export function parseConfig(raw: Record<string, unknown>): AISentinelConfig {
  // Merge env var overrides before parsing
  const merged = { ...raw };
  if (process.env.AI_SENTINEL_API_KEY) {
    merged.apiKey = process.env.AI_SENTINEL_API_KEY;
  }
  if (process.env.AI_SENTINEL_API_URL) {
    merged.apiUrl = process.env.AI_SENTINEL_API_URL;
  }
  return AISentinelConfigSchema.parse(merged);
}

/**
 * Resolve effective config for a specific agent.
 *
 * Returns null if the agent is excluded (caller should skip scanning).
 * Returns config with per-agent overrides merged if an override entry exists.
 * Returns the base config unchanged otherwise.
 */
export function resolveAgentConfig(
  config: AISentinelConfig,
  agentId: string | undefined,
): AISentinelConfig | null {
  if (!agentId) return config;

  if (config.excludeAgents.includes(agentId)) {
    return null;
  }

  const override = config.agentOverrides.find((o) => o.agentId === agentId);
  if (!override) return config;

  return {
    ...config,
    ...(override.mode !== undefined && { mode: override.mode }),
    ...(override.threatThreshold !== undefined && { threatThreshold: override.threatThreshold }),
  };
}
