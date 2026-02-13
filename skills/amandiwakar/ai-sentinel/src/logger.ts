import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
import type { AuditEntry, LogLevel, PluginLogger } from "./types.js";

// =============================================================================
// AI Sentinel — Logger
//
// Writes persistent audit trail to ~/.openclaw/logs/ai-sentinel.log
// Uses api.logger for console output when available, falls back to console.
// =============================================================================

const LOG_DIR = join(homedir(), ".openclaw", "logs");
const LOG_FILE = join(LOG_DIR, "ai-sentinel.log");

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

let currentLevel: LogLevel = "info";
let pluginLogger: PluginLogger | null = null;
let dirEnsured = false;

export function setLogLevel(level: LogLevel): void {
  currentLevel = level;
}

export function setPluginLogger(logger: PluginLogger): void {
  pluginLogger = logger;
}

function shouldLog(level: LogLevel): boolean {
  return LEVEL_ORDER[level] >= LEVEL_ORDER[currentLevel];
}

function formatLine(level: string, message: string): string {
  return `${new Date().toISOString()} [${level.toUpperCase()}] ${message}`;
}

async function ensureDir(): Promise<void> {
  if (dirEnsured) return;
  try {
    await mkdir(LOG_DIR, { recursive: true });
    dirEnsured = true;
  } catch {
    // Directory may already exist
    dirEnsured = true;
  }
}

async function writeToFile(line: string): Promise<void> {
  await ensureDir();
  await appendFile(LOG_FILE, line + "\n", "utf-8");
}

export function debug(message: string): void {
  if (!shouldLog("debug")) return;
  const line = formatLine("debug", message);
  if (pluginLogger) {
    pluginLogger.debug(line);
  }
  writeToFile(line).catch(() => {});
}

export function info(message: string): void {
  if (!shouldLog("info")) return;
  const line = formatLine("info", message);
  if (pluginLogger) {
    pluginLogger.info(line);
  }
  writeToFile(line).catch(() => {});
}

export function warn(message: string): void {
  if (!shouldLog("warn")) return;
  const line = formatLine("warn", message);
  if (pluginLogger) {
    pluginLogger.warn(line);
  }
  writeToFile(line).catch(() => {});
}

export function error(message: string): void {
  if (!shouldLog("error")) return;
  const line = formatLine("error", message);
  if (pluginLogger) {
    pluginLogger.error(line);
  }
  writeToFile(line).catch(() => {});
}

export async function audit(entry: AuditEntry): Promise<void> {
  await ensureDir();
  const line = JSON.stringify(entry);
  await appendFile(LOG_FILE, line + "\n", "utf-8");
}
