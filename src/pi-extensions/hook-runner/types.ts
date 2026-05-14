import { SYNTHETIC_HOOK_EVENT_NAMES } from "../hook-bridge.js";

export const CORE_HOOK_EVENT_NAMES = [
	"PostToolUse",
	"PostToolUseFailure",
	"SessionStart",
	"SessionEnd",
	"SubagentStart",
	"SubagentStop",
	"UserPromptSubmit",
	"Stop",
	"Notification",
	"PreCompact",
	"PostCompact",
] as const;

export const HOOK_EVENT_NAMES = [...SYNTHETIC_HOOK_EVENT_NAMES, ...CORE_HOOK_EVENT_NAMES] as const;

export type HookEventName = (typeof HOOK_EVENT_NAMES)[number];

export function isHookEventName(value: unknown): value is HookEventName {
	return typeof value === "string" && (HOOK_EVENT_NAMES as readonly string[]).includes(value);
}

export type HookSource = "bundled" | "global" | "project";

/** Wire shape parsed verbatim from hooks.json (bundled or user-supplied). */
export interface HookEntryConfig {
	type: "command";
	command: string;
	/** Seconds; default varies by event family. */
	timeout?: number;
	/** Fire-and-forget — runHookAsync does not block the dispatcher. */
	async?: boolean;
}

/** Loaded view of a hook entry: parsed config + runtime tagging. */
export interface HookEntryRuntime {
	config: HookEntryConfig;
	source: HookSource;
	disabled: boolean;
}

export interface HookGroup {
	/** Regex matched case-insensitively against the CC-style tool name. undefined = match all. */
	matcher?: string;
	hooks: HookEntryRuntime[];
}

export interface HooksConfig {
	PreToolUse?: HookGroup[];
	PostToolUse?: HookGroup[];
	PostToolUseFailure?: HookGroup[];
	PostToolBatch?: HookGroup[];
	SessionStart?: HookGroup[];
	Setup?: HookGroup[];
	SessionEnd?: HookGroup[];
	SubagentStart?: HookGroup[];
	SubagentStop?: HookGroup[];
	UserPromptSubmit?: HookGroup[];
	UserPromptExpansion?: HookGroup[];
	Stop?: HookGroup[];
	StopFailure?: HookGroup[];
	TeammateIdle?: HookGroup[];
	InstructionsLoaded?: HookGroup[];
	ConfigChange?: HookGroup[];
	CwdChanged?: HookGroup[];
	FileChanged?: HookGroup[];
	PreCompact?: HookGroup[];
	PostCompact?: HookGroup[];
	Notification?: HookGroup[];
	PermissionRequest?: HookGroup[];
	PermissionDenied?: HookGroup[];
	TaskCreated?: HookGroup[];
	TaskCompleted?: HookGroup[];
	WorktreeCreate?: HookGroup[];
	WorktreeRemove?: HookGroup[];
	Elicitation?: HookGroup[];
	ElicitationResult?: HookGroup[];
	[key: string]: HookGroup[] | undefined;
}

export interface HookRunResult {
	exitCode: number;
	stdout: string;
	stderr: string;
	timedOut: boolean;
}

export interface HookRunnerOptions {
	disableBundledHooks?: boolean;
	/** Command basenames to skip. */
	disabledHooks?: string[];
}

export function isRecord(value: unknown): value is Record<string, unknown> {
	return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}
