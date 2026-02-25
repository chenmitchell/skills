export const SCHEMA_VERSION = 3;

// ---------------------------------------------------------------------------
// Table definitions — Phase 1
// ---------------------------------------------------------------------------

export const CREATE_SCHEMA_META_TABLE = `
CREATE TABLE IF NOT EXISTS schema_meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
`;

/** Raw conversation segments (one row per flushed buffer) */
export const CREATE_CONVERSATIONS_TABLE = `
CREATE TABLE IF NOT EXISTS conversations (
  id          TEXT    PRIMARY KEY,
  agent_id    TEXT    NOT NULL,
  session_key TEXT    NOT NULL,
  channel     TEXT,
  started_at  INTEGER NOT NULL,
  ended_at    INTEGER NOT NULL,
  turn_count  INTEGER NOT NULL,
  raw_text    TEXT    NOT NULL,
  metadata    TEXT
);
`;

/** Individual messages within a conversation segment */
export const CREATE_MESSAGES_TABLE = `
CREATE TABLE IF NOT EXISTS messages (
  id              TEXT    PRIMARY KEY,
  conversation_id TEXT    NOT NULL REFERENCES conversations(id),
  role            TEXT    NOT NULL,
  content         TEXT    NOT NULL,
  timestamp       INTEGER NOT NULL,
  message_id      TEXT,
  metadata        TEXT
);
`;

export const CREATE_CONVERSATIONS_IDX = `
CREATE INDEX IF NOT EXISTS idx_conversations_session_key
  ON conversations(session_key);
`;

export const CREATE_MESSAGES_IDX = `
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
  ON messages(conversation_id);
`;

// ---------------------------------------------------------------------------
// Table definitions — Phase 2: Knowledge Base
// ---------------------------------------------------------------------------

/** Extracted facts — the structured knowledge base */
export const CREATE_FACTS_TABLE = `
CREATE TABLE IF NOT EXISTS facts (
  id              TEXT    PRIMARY KEY,
  agent_id        TEXT    NOT NULL,
  category        TEXT    NOT NULL,
  content         TEXT    NOT NULL,
  summary         TEXT,
  visibility      TEXT    NOT NULL DEFAULT 'shared',
  confidence      REAL    DEFAULT 1.0,
  first_seen_at   INTEGER NOT NULL,
  last_seen_at    INTEGER NOT NULL,
  occurrence_count INTEGER DEFAULT 0,
  supersedes      TEXT,
  is_active       INTEGER DEFAULT 1,
  metadata        TEXT
);
`;

/** Fact occurrences — temporal tracking for each mention */
export const CREATE_FACT_OCCURRENCES_TABLE = `
CREATE TABLE IF NOT EXISTS fact_occurrences (
  id              TEXT    PRIMARY KEY,
  fact_id         TEXT    NOT NULL REFERENCES facts(id),
  conversation_id TEXT    NOT NULL REFERENCES conversations(id),
  timestamp       INTEGER NOT NULL,
  context_snippet TEXT,
  sentiment       TEXT
);
`;

/** Extraction log — tracks which conversations have been processed */
export const CREATE_EXTRACTION_LOG_TABLE = `
CREATE TABLE IF NOT EXISTS extraction_log (
  conversation_id   TEXT    PRIMARY KEY REFERENCES conversations(id),
  extracted_at      INTEGER NOT NULL,
  model_used        TEXT    NOT NULL,
  facts_extracted   INTEGER DEFAULT 0,
  facts_updated     INTEGER DEFAULT 0,
  facts_deduplicated INTEGER DEFAULT 0,
  error             TEXT
);
`;

// Phase 2 indexes
export const CREATE_FACTS_AGENT_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_agent_id ON facts(agent_id);
`;
export const CREATE_FACTS_CATEGORY_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
`;
export const CREATE_FACTS_VISIBILITY_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_visibility ON facts(visibility);
`;
export const CREATE_FACTS_ACTIVE_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_is_active ON facts(is_active);
`;
export const CREATE_FACT_OCCURRENCES_FACT_IDX = `
CREATE INDEX IF NOT EXISTS idx_fact_occurrences_fact_id ON fact_occurrences(fact_id);
`;

// FTS5 virtual table for full-text search over fact content + summary.
// Uses external content table (content=facts) so the text is NOT duplicated —
// the FTS index only stores the inverted index. Triggers below keep it in sync.
export const CREATE_FACTS_FTS_TABLE = `
CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
  content,
  summary,
  content=facts,
  content_rowid=rowid
);
`;

// Keep facts_fts in sync with the facts table
export const CREATE_FACTS_FTS_INSERT_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_ai AFTER INSERT ON facts BEGIN
  INSERT INTO facts_fts(rowid, content, summary)
    VALUES (new.rowid, new.content, COALESCE(new.summary, ''));
END;
`;

export const CREATE_FACTS_FTS_DELETE_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_ad AFTER DELETE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, content, summary)
    VALUES ('delete', old.rowid, old.content, COALESCE(old.summary, ''));
END;
`;

export const CREATE_FACTS_FTS_UPDATE_TRIGGER = `
CREATE TRIGGER IF NOT EXISTS facts_fts_au AFTER UPDATE ON facts BEGIN
  INSERT INTO facts_fts(facts_fts, rowid, content, summary)
    VALUES ('delete', old.rowid, old.content, COALESCE(old.summary, ''));
  INSERT INTO facts_fts(rowid, content, summary)
    VALUES (new.rowid, new.content, COALESCE(new.summary, ''));
END;
`;

// ---------------------------------------------------------------------------
// Schema migration v2 → v3: Add embedding column to facts
// ---------------------------------------------------------------------------

/**
 * Add embedding BLOB column to facts table.
 * Stores Float32Array as raw bytes for compact storage.
 * ALTER TABLE IF NOT EXISTS not supported in SQLite — handled in migration code.
 */
export const MIGRATE_V2_TO_V3 = `
ALTER TABLE facts ADD COLUMN embedding BLOB;
`;

export const CREATE_FACTS_EMBEDDING_IDX = `
CREATE INDEX IF NOT EXISTS idx_facts_has_embedding
  ON facts(agent_id, is_active) WHERE embedding IS NOT NULL;
`;

// ---------------------------------------------------------------------------
// All DDL statements to run on first boot (idempotent)
// ---------------------------------------------------------------------------

/** All DDL statements to run on first boot (idempotent) */
export const ALL_DDL = [
  // Phase 1
  CREATE_SCHEMA_META_TABLE,
  CREATE_CONVERSATIONS_TABLE,
  CREATE_MESSAGES_TABLE,
  CREATE_CONVERSATIONS_IDX,
  CREATE_MESSAGES_IDX,
  // Phase 2
  CREATE_FACTS_TABLE,
  CREATE_FACT_OCCURRENCES_TABLE,
  CREATE_EXTRACTION_LOG_TABLE,
  CREATE_FACTS_AGENT_IDX,
  CREATE_FACTS_CATEGORY_IDX,
  CREATE_FACTS_VISIBILITY_IDX,
  CREATE_FACTS_ACTIVE_IDX,
  CREATE_FACT_OCCURRENCES_FACT_IDX,
  CREATE_FACTS_FTS_TABLE,
  CREATE_FACTS_FTS_INSERT_TRIGGER,
  CREATE_FACTS_FTS_DELETE_TRIGGER,
  CREATE_FACTS_FTS_UPDATE_TRIGGER,
];

// ---------------------------------------------------------------------------
// Row types — Phase 1
// ---------------------------------------------------------------------------

export type ConversationRow = {
  id: string;
  agent_id: string;
  session_key: string;
  channel: string | null;
  started_at: number;
  ended_at: number;
  turn_count: number;
  raw_text: string;
  metadata: string | null;
};

export type MessageRow = {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  timestamp: number;
  message_id: string | null;
  metadata: string | null;
};

// ---------------------------------------------------------------------------
// Row types — Phase 2
// ---------------------------------------------------------------------------

export type FactRow = {
  id: string;
  agent_id: string;
  category: string;
  content: string;
  summary: string | null;
  visibility: string;
  confidence: number;
  first_seen_at: number;
  last_seen_at: number;
  occurrence_count: number;
  supersedes: string | null;
  is_active: number; // 1 = active, 0 = superseded
  metadata: string | null;
  embedding: Buffer | null; // Float32Array stored as raw bytes
};

export type FactOccurrenceRow = {
  id: string;
  fact_id: string;
  conversation_id: string;
  timestamp: number;
  context_snippet: string | null;
  sentiment: string | null;
};

export type ExtractionLogRow = {
  conversation_id: string;
  extracted_at: number;
  model_used: string;
  facts_extracted: number;
  facts_updated: number;
  facts_deduplicated: number;
  error: string | null;
};
