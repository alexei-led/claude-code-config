import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

/** Event-bus channel used by extensions to invoke hook-runner synthetic hook dispatch. */
export const HOOK_RUNNER_INVOKE_CHANNEL = "cc-hooks:invoke";

/**
 * Pi tool name (lowercase, snake_case) → CC tool name (PascalCase or domain-specific).
 *
 * Lives here so every consumer that needs a CC name uses the same mapping —
 * hook-runner's dispatcher, permission-gate's PermissionRequest stdin builder,
 * and plan-mode's ExitPlanMode synthetic invocation all share this table.
 */
const TOOL_NAME_MAP: Record<string, string> = {
	bash: "Bash",
	write: "Write",
	edit: "Edit",
	multiedit: "MultiEdit",
	read: "Read",
	grep: "Grep",
	find: "Glob",
	ls: "Ls",
	subagent: "Agent",
	ask_user_question: "AskUserQuestion",
	exit_plan_mode: "ExitPlanMode",
};

/**
 * Resolve a Pi tool name to its CC equivalent.
 *
 * Unregistered lowercase names fall back to capitalize-first-letter to match
 * legacy behaviour (`finder` → `Finder`). Anything containing underscores or
 * already-mixed case is returned as-is — explicit registration is required
 * for those, so callers get a stable name rather than silent inference.
 */
export function toCcToolName(piName: string): string {
	const mapped = TOOL_NAME_MAP[piName.toLowerCase()];
	if (mapped !== undefined) return mapped;
	if (piName === piName.toLowerCase() && !piName.includes("_")) {
		return piName.charAt(0).toUpperCase() + piName.slice(1);
	}
	return piName;
}

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
 * Margin added on top of the per-subprocess timeout when deriving the outer
 * wait — gives hook-runner room to schedule the callback after its own timer
 * fires.
 */
export const SYNTHETIC_HOOK_OUTER_WAIT_MARGIN_MS = 30_000;

/** Default per-subprocess timeout when neither caller nor hook entry sets one. */
export const SYNTHETIC_HOOK_DEFAULT_TIMEOUT_SEC = 10;

/**
 * Shared synthetic-hook caller for extensions.
 *
 * Two timeouts apply:
 * - `timeoutSec` bounds the hook subprocess inside hook-runner. Forwarded to
 *   hook-runner; individual hook entries with their own `timeout` field
 *   override this per-entry. Default 10s.
 * - `timeoutMs` is the outer wait on this side for hook-runner to call back.
 *   When omitted it is computed as `timeoutSec * 1000 + SYNTHETIC_HOOK_OUTER_WAIT_MARGIN_MS`
 *   so the per-entry timer reliably fires first. Explicit values smaller
 *   than that floor are clamped up; the outer wait must never preempt the
 *   per-entry deadline or hook-runner returns to a stuck caller with no
 *   blocking result (silent fail-open).
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
		timeoutSec?: number;
		timeoutMs?: number;
		timeoutResult?: SyntheticHookInvocationResult;
	},
): Promise<SyntheticHookInvocationResult> {
	if (!ctx || typeof ctx !== "object") return {};
	if (typeof ctx.sessionManager?.getSessionId?.() !== "string") return {};
	if (typeof ctx.cwd !== "string") return {};
	if (!pi.events || typeof pi.events.emit !== "function") return {};

	const timeoutSec = request.timeoutSec ?? SYNTHETIC_HOOK_DEFAULT_TIMEOUT_SEC;
	// When the caller omits timeoutMs, derive it from timeoutSec so the outer
	// wait survives long-running per-entry hooks (the documented invariant).
	// Explicit caller-supplied values are honored verbatim — short outer waits
	// are valid for interactive flows where waiting on a missing hook-runner
	// response would block the user.
	const timeoutMs = request.timeoutMs ?? timeoutSec * 1000 + SYNTHETIC_HOOK_OUTER_WAIT_MARGIN_MS;

	return await new Promise((resolve) => {
		let settled = false;
		const done = (value: SyntheticHookInvocationResult) => {
			if (settled) return;
			settled = true;
			resolve(value);
		};
		const timer = setTimeout(() => done(request.timeoutResult ?? {}), timeoutMs);
		pi.events.emit(HOOK_RUNNER_INVOKE_CHANNEL, {
			hookEventName: request.hookEventName,
			ccToolName: request.ccToolName,
			stdin: request.stdin,
			timeoutSec,
			onResult: (result: SyntheticHookInvocationResult) => {
				clearTimeout(timer);
				done(result);
			},
		});
	});
}
