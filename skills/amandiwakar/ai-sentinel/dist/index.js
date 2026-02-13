import { parseConfig } from "./config.js";
import { scan } from "./scanner/detector.js";
import { APIReporter } from "./api-reporter.js";
import { createMessageReceivedHook } from "./hooks/message-received.js";
import { createToolResultPersistHook } from "./hooks/tool-result-persist.js";
import { createBeforeToolCallHook } from "./hooks/before-tool-call.js";
import { createBeforeAgentStartHook } from "./hooks/before-agent-start.js";
import * as log from "./logger.js";
// =============================================================================
// AI Sentinel — OpenClaw Plugin Entry Point
//
// Uses the actual OpenClaw Plugin SDK register(api) pattern.
// Hooks are registered via api.on() with priority 100 (high — runs early).
// =============================================================================
const plugin = {
    id: "ai-sentinel",
    name: "AI Sentinel",
    register(api) {
        const config = parseConfig(api.pluginConfig);
        // Initialize logger
        log.setLogLevel(config.logLevel);
        log.setPluginLogger(api.logger);
        log.info(`Initializing AI Sentinel v0.1.1 [mode=${config.mode}, threshold=${config.threatThreshold}]`);
        // Log per-agent configuration
        if (config.excludeAgents.length > 0) {
            log.info(`Excluded agents: ${config.excludeAgents.join(", ")}`);
        }
        if (config.agentOverrides.length > 0) {
            log.info(`Agent overrides: ${config.agentOverrides.map((o) => o.agentId).join(", ")}`);
        }
        // Initialize API reporter if configured
        let reporter = null;
        if (config.apiKey &&
            config.apiUrl &&
            config.reportMode !== "none") {
            reporter = new APIReporter(config);
            log.info(`API reporting enabled [mode=${config.reportMode}] → ${config.apiUrl}`);
        }
        else if (config.reportMode !== "none") {
            log.debug("API reporting not configured (no apiKey). Local-only mode.");
        }
        // Register lifecycle hooks with adapter wrappers
        // The OpenClaw SDK calls hooks with (event, ctx) but our hook functions
        // expect a single payload object. These adapters map SDK field names to
        // our internal payload shape.
        const messageReceivedHook = createMessageReceivedHook(config, api.logger, reporter);
        api.on("message_received", (event, ctx) => messageReceivedHook({
            message: event.content,
            senderId: event.metadata?.senderId ?? event.from,
            channel: ctx.channelId,
            sessionKey: ctx.conversationId,
            agentId: ctx.accountId ?? config.agentId,
        }), { priority: 100 });
        const beforeToolCallHook = createBeforeToolCallHook(config, api.logger, reporter);
        api.on("before_tool_call", (event, ctx) => beforeToolCallHook({
            toolName: event.toolName,
            parameters: event.params,
            sessionKey: ctx.sessionKey,
            agentId: ctx.agentId,
        }), { priority: 100 });
        const toolResultPersistHook = createToolResultPersistHook(config, api.logger, reporter);
        api.on("tool_result_persist", (event, ctx) => toolResultPersistHook({
            toolName: event.toolName,
            result: event.message,
            sessionKey: ctx.sessionKey,
            agentId: ctx.agentId,
        }), { priority: 100 });
        const beforeAgentStartHook = createBeforeAgentStartHook(config);
        api.on("before_agent_start", (event, ctx) => beforeAgentStartHook({
            sessionKey: ctx.sessionKey,
            agentId: ctx.agentId,
        }), { priority: 100 });
        // Register manual scan tool
        api.registerTool({
            name: "ai_sentinel_scan",
            description: "Manually scan text for prompt injection threats. Use when you suspect content may be adversarial.",
            parameters: {
                text: {
                    type: "string",
                    description: "The text to scan for prompt injection patterns",
                    required: true,
                },
                location: {
                    type: "string",
                    description: 'Where the text came from: "message", "tool_result", "tool_params", or "system"',
                    required: false,
                },
            },
            execute(params) {
                const text = params.text;
                const location = params.location ?? "message";
                const result = scan(text, config, { location });
                return JSON.stringify(result, null, 2);
            },
        });
        log.info("AI Sentinel plugin registered successfully");
    },
};
export default plugin;
//# sourceMappingURL=index.js.map