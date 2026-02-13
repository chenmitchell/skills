import type { AISentinelConfig, ScanResult, ScanLocation } from "../types.js";
export interface ScanOptions {
    location?: ScanLocation;
}
export declare function scan(text: string, config: AISentinelConfig, opts?: ScanOptions): ScanResult;
/**
 * Recursively extract all string values from a nested object/array.
 * Used to scan structured tool results for embedded threats.
 */
export declare function extractText(value: unknown): string;
//# sourceMappingURL=detector.d.ts.map