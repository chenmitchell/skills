import * as log from "./logger.js";

const seenAgents = new Set<string>();

/**
 * Track an agent by ID. Returns true if the agent was newly seen.
 */
export function trackAgent(agentId: string | undefined): boolean {
  if (!agentId) return false;
  if (seenAgents.has(agentId)) return false;

  seenAgents.add(agentId);
  log.info(`New agent discovered: ${agentId}`);
  return true;
}

export function getSeenAgents(): Set<string> {
  return new Set(seenAgents);
}

export function clearSeenAgents(): void {
  seenAgents.clear();
}
