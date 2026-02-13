import type { AISentinelConfig, ScanResult } from "./types.js";
export interface TelemetryEvent {
    eventId: string;
    timestamp: string;
    instanceId: string;
    pluginVersion: string;
    eventType: string;
    agentId?: string;
    sessionKey: string;
    channel?: string;
    threats: Array<{
        category: string;
        pattern: string;
        confidence: number;
        location: string;
        matchedPreview?: string;
    }>;
    highestConfidence: number;
    action: string;
    scanTimeMs: number;
    rawInput?: string;
}
export interface ReportContext {
    sessionKey: string;
    channel?: string;
    senderId?: string;
    toolName?: string;
    agentId?: string;
    location: string;
}
export declare class APIReporter {
    private config;
    private instanceId;
    private batch;
    private flushTimer;
    private disabled;
    private consecutiveFailures;
    private retryDelayMs;
    constructor(config: AISentinelConfig);
    /**
     * Report a scan event. Dispatches to telemetry or cloud-scan based on config.
     */
    report(eventType: string, rawText: string, scanResult: ScanResult | null, ctx: ReportContext): void;
    /**
     * Telemetry mode: queue event for batch flush.
     */
    private reportTelemetry;
    /**
     * Cloud-scan mode: send raw text to API scan endpoints.
     */
    private reportCloudScan;
    /**
     * Flush batched telemetry events to API.
     */
    flush(): Promise<void>;
    /**
     * Fire-and-forget HTTP request with timeout and self-disable on auth errors.
     */
    private sendRequest;
    /**
     * Stop the flush timer and send any remaining events.
     */
    shutdown(): Promise<void>;
}
//# sourceMappingURL=api-reporter.d.ts.map