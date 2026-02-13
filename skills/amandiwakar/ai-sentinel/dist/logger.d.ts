import type { AuditEntry, LogLevel, PluginLogger } from "./types.js";
export declare function setLogLevel(level: LogLevel): void;
export declare function setPluginLogger(logger: PluginLogger): void;
export declare function debug(message: string): void;
export declare function info(message: string): void;
export declare function warn(message: string): void;
export declare function error(message: string): void;
export declare function audit(entry: AuditEntry): Promise<void>;
//# sourceMappingURL=logger.d.ts.map