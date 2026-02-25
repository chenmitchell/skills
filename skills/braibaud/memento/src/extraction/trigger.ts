/**
 * Extraction Trigger
 *
 * Called by the segment writer after a conversation segment is saved to SQLite.
 * Runs fact extraction asynchronously so it never blocks the message flow.
 *
 * Responsibilities:
 *   - Skip segments that are too short (configurable minTurnsForExtraction)
 *   - Rate-limit extraction calls (configurable maxExtractionsPerMinute)
 *   - Fetch existing facts for dedup context
 *   - Call the LLM extractor
 *   - Run deduplication
 *   - Log the result (success or error) to extraction_log
 *
 * All errors are caught and logged — this code must never crash the plugin.
 */

import type { ConversationDB, ExtractionLogResult } from "../storage/db.js";
import type { ExtractionConfig } from "../config.js";
import type { ConversationRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";
import { extractFacts } from "./extractor.js";
import { processExtractedFacts } from "./deduplicator.js";

export class ExtractionTrigger {
  /** How many extractions have fired in the current 60-second window */
  private extractionsThisMinute = 0;
  /** Timestamp when the current rate-limit window started */
  private minuteWindowStart = Date.now();

  constructor(
    private readonly db: ConversationDB,
    private readonly cfg: ExtractionConfig,
    /** Full model string, e.g. "anthropic/claude-sonnet-4-6" */
    private readonly extractionModel: string,
    private readonly logger: PluginLogger,
  ) {}

  /**
   * Schedule extraction for a captured conversation segment.
   * Returns immediately — extraction runs in the next event-loop tick.
   */
  triggerAsync(conversation: ConversationRow): void {
    setImmediate(() => {
      this.runExtraction(conversation).catch((err) => {
        this.logger.warn(
          `memento: unhandled extraction error for ${conversation.id}: ${String(err)}`,
        );
      });
    });
  }

  // ---- Private ------------------------------------------------------------

  private async runExtraction(conversation: ConversationRow): Promise<void> {
    // Skip segments that are too short to yield useful facts
    if (conversation.turn_count < this.cfg.minTurnsForExtraction) {
      this.logger.debug?.(
        `memento: skipping extraction for ${conversation.id} — ` +
          `only ${conversation.turn_count} turns (min: ${this.cfg.minTurnsForExtraction})`,
      );
      return;
    }

    // Reset rate-limit window every 60 seconds
    const now = Date.now();
    if (now - this.minuteWindowStart >= 60_000) {
      this.extractionsThisMinute = 0;
      this.minuteWindowStart = now;
    }

    if (this.extractionsThisMinute >= this.cfg.maxExtractionsPerMinute) {
      this.logger.warn(
        `memento: extraction rate limit reached (${this.cfg.maxExtractionsPerMinute}/min), ` +
          `skipping segment ${conversation.id}`,
      );
      return;
    }
    this.extractionsThisMinute++;

    this.logger.debug?.(
      `memento: starting extraction for ${conversation.id} ` +
        `(${conversation.turn_count} turns, agent: ${conversation.agent_id})`,
    );

    try {
      // Fetch existing active facts for dedup context
      const existingFacts = this.db.getRelevantFacts(
        conversation.agent_id,
        this.cfg.includeExistingFactsCount,
      );

      // Call the LLM
      const extractionResult = await extractFacts(
        conversation,
        existingFacts,
        this.extractionModel,
        this.logger,
      );

      if (extractionResult.error) {
        this.logger.warn(
          `memento: extraction failed for ${conversation.id}: ${extractionResult.error}`,
        );
        this.logResult(conversation.id, {
          modelUsed: extractionResult.modelUsed,
          factsExtracted: 0,
          factsUpdated: 0,
          factsDeduplicated: 0,
          error: extractionResult.error,
        });
        return;
      }

      if (extractionResult.facts.length === 0) {
        this.logger.debug?.(
          `memento: no facts extracted from ${conversation.id}`,
        );
        this.logResult(conversation.id, {
          modelUsed: extractionResult.modelUsed,
          factsExtracted: 0,
          factsUpdated: 0,
          factsDeduplicated: 0,
          error: null,
        });
        return;
      }

      // Deduplicate and persist
      const dedup = processExtractedFacts(
        extractionResult.facts,
        conversation.id,
        conversation.agent_id,
        this.db,
        this.logger,
      );

      this.logResult(conversation.id, {
        modelUsed: extractionResult.modelUsed,
        ...dedup,
        error: null,
      });

      this.logger.info(
        `memento: [${conversation.id}] extracted ` +
          `${dedup.factsExtracted} new, ` +
          `${dedup.factsUpdated} updated, ` +
          `${dedup.factsDeduplicated} deduplicated ` +
          `(agent: ${conversation.agent_id})`,
      );
    } catch (err) {
      const errMsg = String(err);
      this.logger.warn(
        `memento: extraction threw for ${conversation.id}: ${errMsg}`,
      );
      this.logResult(conversation.id, {
        modelUsed: this.extractionModel,
        factsExtracted: 0,
        factsUpdated: 0,
        factsDeduplicated: 0,
        error: errMsg,
      });
    }
  }

  private logResult(
    conversationId: string,
    result: ExtractionLogResult,
  ): void {
    try {
      this.db.logExtraction(conversationId, result);
    } catch (err) {
      this.logger.warn(
        `memento: failed to log extraction result for ${conversationId}: ${String(err)}`,
      );
    }
  }
}
