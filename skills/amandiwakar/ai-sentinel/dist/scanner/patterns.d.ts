import type { ThreatCategory } from "../types.js";
export interface ThreatPattern {
    id: string;
    regex: RegExp;
    category: ThreatCategory;
    confidence: number;
    description: string;
}
export declare const THREAT_PATTERNS: ThreatPattern[];
export declare const TOOL_RESULT_BOOST_CATEGORIES: ThreatCategory[];
export declare const TOOL_RESULT_CONFIDENCE_BOOST = 0.15;
//# sourceMappingURL=patterns.d.ts.map