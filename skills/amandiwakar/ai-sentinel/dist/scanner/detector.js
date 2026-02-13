import { THREAT_PATTERNS, TOOL_RESULT_BOOST_CATEGORIES, TOOL_RESULT_CONFIDENCE_BOOST, } from "./patterns.js";
export function scan(text, config, opts = {}) {
    const start = performance.now();
    const location = opts.location ?? "message";
    const threats = [];
    for (const pattern of THREAT_PATTERNS) {
        const match = pattern.regex.exec(text);
        if (!match)
            continue;
        let confidence = pattern.confidence;
        // Boost confidence for certain categories when scanning tool results
        if (location === "tool_result" &&
            TOOL_RESULT_BOOST_CATEGORIES.includes(pattern.category)) {
            confidence = Math.min(1, confidence + TOOL_RESULT_CONFIDENCE_BOOST);
        }
        threats.push({
            patternId: pattern.id,
            category: pattern.category,
            confidence,
            description: pattern.description,
            matchedText: match[0].slice(0, 100),
        });
    }
    const scanTimeMs = performance.now() - start;
    const highestConfidence = threats.length > 0
        ? Math.max(...threats.map((t) => t.confidence))
        : 0;
    const action = determineAction(threats, config, highestConfidence);
    const safe = threats.length === 0;
    const summary = safe
        ? "No threats detected"
        : `${threats.length} threat(s) detected: ${[...new Set(threats.map((t) => t.category))].join(", ")} (max confidence: ${(highestConfidence * 100).toFixed(0)}%)`;
    return { safe, action, threats, highestConfidence, summary, scanTimeMs };
}
function determineAction(threats, config, highestConfidence) {
    if (threats.length === 0)
        return "allow";
    if (config.mode === "enforce" && highestConfidence >= config.threatThreshold) {
        return "block";
    }
    if (highestConfidence >= config.threatThreshold) {
        return "warn";
    }
    return "allow";
}
/**
 * Recursively extract all string values from a nested object/array.
 * Used to scan structured tool results for embedded threats.
 */
export function extractText(value) {
    if (typeof value === "string")
        return value;
    if (value == null)
        return "";
    if (Array.isArray(value)) {
        return value.map(extractText).filter(Boolean).join("\n");
    }
    if (typeof value === "object") {
        return Object.values(value)
            .map(extractText)
            .filter(Boolean)
            .join("\n");
    }
    return String(value);
}
//# sourceMappingURL=detector.js.map