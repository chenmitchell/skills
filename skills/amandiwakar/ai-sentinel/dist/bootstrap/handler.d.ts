interface BootstrapFile {
    path: string;
    content: string;
    role: string;
}
interface HookEvent {
    type: string;
    action: string;
    sessionKey: string;
    timestamp: Date;
    messages: string[];
    context: {
        bootstrapFiles?: BootstrapFile[];
        workspaceDir?: string;
        cfg?: unknown;
        [key: string]: unknown;
    };
}
declare const handler: (event: HookEvent) => Promise<void>;
export default handler;
