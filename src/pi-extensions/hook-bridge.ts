import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

/** Event-bus channel used by extensions to invoke hook-runner synthetic hook dispatch. */
export const HOOK_RUNNER_INVOKE_CHANNEL = "cc-hooks:invoke";

/** Synthetic hook event names accepted by hook-runner bridge invocations. */
export const SYNTHETIC_HOOK_EVENT_NAMES = [
	"PreToolUse",
	"PermissionRequest",
	"PermissionDenied",
	"TaskCreated",
	"TaskCompleted",
	"PostToolBatch",
	"UserPromptExpansion",
	"Setup",
	"StopFailure",
	"TeammateIdle",
	"InstructionsLoaded",
	"ConfigChange",
	"CwdChanged",
	"FileChanged",
	"WorktreeCreate",
	"WorktreeRemove",
	"Elicitation",
	"ElicitationResult",
] as const;

export type SyntheticHookEventName = (typeof SYNTHETIC_HOOK_EVENT_NAMES)[number];

type SyntheticHookBaseResult = {
	blocked?: boolean;
	reason?: string;
	updatedInput?: Record<string, unknown>;
	additionalContext?: string;
	worktreePath?: string;
};

type SyntheticPreToolUseResult = SyntheticHookBaseResult & {
	decision?: "allow" | "ask" | "deny" | "defer";
	behavior?: never;
	retry?: never;
	message?: never;
	interrupt?: never;
};

type SyntheticPermissionRequestResult = SyntheticHookBaseResult & {
	behavior?: "allow" | "deny";
	message?: string;
	interrupt?: boolean;
	decision?: never;
	retry?: never;
};

type SyntheticPermissionDeniedResult = SyntheticHookBaseResult & {
	retry?: boolean;
	decision?: never;
	behavior?: never;
	message?: never;
	interrupt?: never;
};

type SyntheticGenericResult = SyntheticHookBaseResult & {
	decision?: never;
	behavior?: never;
	retry?: never;
	message?: never;
	interrupt?: never;
};

export type SyntheticHookInvocationResult =
	| SyntheticPreToolUseResult
	| SyntheticPermissionRequestResult
	| SyntheticPermissionDeniedResult
	| SyntheticGenericResult;

export interface SyntheticHookInvocationRequest {
	hookEventName: SyntheticHookEventName;
	stdin: Record<string, unknown>;
	ccToolName?: string;
	timeoutSec?: number;
	onResult?: (result: SyntheticHookInvocationResult) => void;
}

/**
 * Shared synthetic-hook caller for extensions.
 *
 * Returns `timeoutResult` when hook-runner does not respond before `timeoutMs`.
 * Returns `{}` when context/session/event bus is unavailable.
 */
export async function invokeSyntheticHook(
	pi: ExtensionAPI,
	ctx: ExtensionContext,
	request: {
		hookEventName: SyntheticHookEventName;
		stdin: Record<string, unknown>;
		ccToolName?: string;
		timeoutMs?: number;
		timeoutResult?: SyntheticHookInvocationResult;
	},
): Promise<SyntheticHookInvocationResult> {
	if (!ctx || typeof ctx !== "object") return {};
	if (typeof ctx.sessionManager?.getSessionId?.() !== "string") return {};
	if (typeof ctx.cwd !== "string") return {};
	if (!pi.events || typeof pi.events.emit !== "function") return {};

	return await new Promise((resolve) => {
		let settled = false;
		const done = (value: SyntheticHookInvocationResult) => {
			if (settled) return;
			settled = true;
			resolve(value);
		};
		const timer = setTimeout(() => done(request.timeoutResult ?? {}), request.timeoutMs ?? 2000);
		pi.events.emit(HOOK_RUNNER_INVOKE_CHANNEL, {
			hookEventName: request.hookEventName,
			ccToolName: request.ccToolName,
			stdin: request.stdin,
			onResult: (result: SyntheticHookInvocationResult) => {
				clearTimeout(timer);
				done(result);
			},
		});
	});
}
