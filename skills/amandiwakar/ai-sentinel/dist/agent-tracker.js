import * as log from "./logger.js";
const seenAgents = new Set();
/**
 * Track an agent by ID. Returns true if the agent was newly seen.
 */
export function trackAgent(agentId) {
    if (!agentId)
        return false;
    if (seenAgents.has(agentId))
        return false;
    seenAgents.add(agentId);
    log.info(`New agent discovered: ${agentId}`);
    return true;
}
export function getSeenAgents() {
    return new Set(seenAgents);
}
export function clearSeenAgents() {
    seenAgents.clear();
}
//# sourceMappingURL=agent-tracker.js.map