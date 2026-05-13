/**
 * Hook Runner — bridges Pi extension events to CC-compatible hook scripts.
 *
 * Built-in wiring dispatches to dist/pi/hooks/ scripts (file-protector, git-guardrails,
 * skill-enforcer, session-start, smart-lint, test-runner) and ccgram for session tracking.
 * User hooks in ~/.pi/agent/settings.json or .pi/settings.json are merged additive on top.
 *
 * Design inspired by pi-hooks (MIT, https://github.com/hsingjui/pi-hooks).
 * Differences: English error messages, async field honoured, correct compact trigger, typed.
 */

import type {
	AgentEndEvent,
	AgentStartEvent,
	BeforeAgentStartEvent,
	BeforeAgentStartEventResult,
	ExtensionAPI,
	ExtensionContext,
	SessionBeforeCompactEvent,
	SessionBeforeCompactResult,
	SessionCompactEvent,
	SessionShutdownEvent,
	SessionStartEvent,
	ToolCallEvent,
	ToolCallEventResult,
	ToolResultEvent,
	ToolResultEventResult,
} from "@mariozechner/pi-coding-agent";
import { execFile } from "node:child_process";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------------------
// Path resolution — works regardless of where Pi cloned the package
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// dist/pi/extensions/hook-runner.ts → ../hooks → dist/pi/hooks
const HOOKS_DIR = join(__dirname, "..", "hooks");

function hookPath(script: string): string {
	return join(HOOKS_DIR, script);
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface HookEntry {
	type: "command";
	command: string;
	timeout?: number; // seconds; default varies by hook family
	async?: boolean; // fire-and-forget (PostToolUse only)
}

interface HookGroup {
	matcher?: string; // regex matched against CC-style tool name; undefined = match all
	hooks: HookEntry[];
}

interface HooksConfig {
	PreToolUse?: HookGroup[];
	PostToolUse?: HookGroup[];
	PostToolUseFailure?: HookGroup[];
	SessionStart?: HookGroup[];
	SessionEnd?: HookGroup[];
	SubagentStart?: HookGroup[];
	SubagentStop?: HookGroup[];
	UserPromptSubmit?: HookGroup[];
	Stop?: HookGroup[];
	PreCompact?: HookGroup[];
	PostCompact?: HookGroup[];
	[key: string]: HookGroup[] | undefined; // extensible for user configs
}

interface HookRunResult {
	exitCode: number;
	stdout: string;
	stderr: string;
	timedOut: boolean;
}

// ---------------------------------------------------------------------------
// Built-in hook wiring
// ---------------------------------------------------------------------------

const BUILTIN_HOOKS: HooksConfig = {
	SessionStart: [
		{ hooks: [{ type: "command", command: hookPath("session-start.py"), timeout: 5 }] },
		// ccgram: session tracking — async so it never delays the session start
		{ hooks: [{ type: "command", command: "ccgram hook", timeout: 5, async: true }] },
	],
	SessionEnd: [{ hooks: [{ type: "command", command: "ccgram hook", timeout: 5, async: true }] }],
	SubagentStart: [{ hooks: [{ type: "command", command: "ccgram hook", timeout: 5, async: true }] }],
	SubagentStop: [{ hooks: [{ type: "command", command: "ccgram hook", timeout: 5, async: true }] }],
	UserPromptSubmit: [{ hooks: [{ type: "command", command: hookPath("skill-enforcer.sh"), timeout: 15 }] }],
	PreToolUse: [
		{
			matcher: "Write|Edit|MultiEdit",
			hooks: [{ type: "command", command: hookPath("file-protector.py"), timeout: 10 }],
		},
		{
			matcher: "Bash",
			hooks: [{ type: "command", command: hookPath("git-guardrails.sh"), timeout: 10 }],
		},
	],
	PostToolUse: [
		{
			matcher: "Write|Edit|MultiEdit",
			hooks: [
				// sync: inject lint errors into tool result so LLM sees and fixes them
				{ type: "command", command: hookPath("smart-lint.sh"), timeout: 60, async: false },
				// async: tests are slow; fire-and-forget, notify user on exit 2
				{ type: "command", command: hookPath("test-runner.sh"), timeout: 120, async: true },
			],
		},
	],
	Stop: [{ hooks: [{ type: "command", command: "ccgram hook", timeout: 5, async: true }] }],
};

// ---------------------------------------------------------------------------
// Tool name normalisation: Pi lowercase → CC CamelCase
// ---------------------------------------------------------------------------

const TOOL_NAME_MAP: Record<string, string> = {
	bash: "Bash",
	write: "Write",
	edit: "Edit",
	multiedit: "MultiEdit",
	read: "Read",
	grep: "Grep",
	find: "Find",
	ls: "Ls",
};

function toCcToolName(piName: string): string {
	return TOOL_NAME_MAP[piName.toLowerCase()] ?? (piName === piName.toLowerCase() ? piName.charAt(0).toUpperCase() + piName.slice(1) : piName);
}

// ---------------------------------------------------------------------------
// Config loading (lazy — on first session_start)
// ---------------------------------------------------------------------------

let _config: HooksConfig | null = null;
let _configLoadedForCwd = "";
let _ifWarningShown = false;

function mergeHooks(base: HooksConfig, user: HooksConfig): void {
	for (const [key, groups] of Object.entries(user)) {
		if (!groups) continue;
		const existing = base[key];
		base[key] = existing ? [...existing, ...groups] : [...groups];
	}
}

function loadConfig(cwd: string): void {
	if (_config && _configLoadedForCwd === cwd) return;
	_config = structuredClone(BUILTIN_HOOKS);
	_configLoadedForCwd = cwd;

	const configPaths = [join(homedir(), ".pi", "agent", "settings.json"), join(cwd, ".pi", "settings.json")];

	for (const configPath of configPaths) {
		try {
			const raw = readFileSync(configPath, "utf-8");
			const parsed: { hooks?: HooksConfig } = JSON.parse(raw);
			if (parsed.hooks) {
				mergeHooks(_config, parsed.hooks);
				// Warn once if user config uses unsupported 'if' predicate field
				if (!_ifWarningShown) {
					const hasIf = Object.values(parsed.hooks)
						.flat()
						.flatMap((g) => g?.hooks ?? [])
						.some((h) => "if" in h);
					if (hasIf) {
						_ifWarningShown = true;
						console.warn("[hook-runner] 'if' predicate in hooks config is not supported in v1; use 'matcher' instead");
					}
				}
			}
		} catch {
			// File absent or malformed: silently skip
		}
	}
}

function resolvedConfig(): HooksConfig {
	return _config ?? BUILTIN_HOOKS;
}

// ---------------------------------------------------------------------------
// Matcher evaluation
// ---------------------------------------------------------------------------

function matcherMatches(matcher: string | undefined, ccToolName: string): boolean {
	if (!matcher || matcher === "" || matcher === "*") return true;
	try {
		return new RegExp(matcher, "i").test(ccToolName);
	} catch {
		return matcher.toLowerCase() === ccToolName.toLowerCase();
	}
}

function matchingGroups(groups: HookGroup[], ccToolName: string): HookGroup[] {
	return groups.filter((g) => matcherMatches(g.matcher, ccToolName));
}

// ---------------------------------------------------------------------------
// Hook execution
// ---------------------------------------------------------------------------

function runHook(entry: HookEntry, stdinJson: string, defaultTimeoutSec = 30): Promise<HookRunResult> {
	return new Promise((resolve) => {
		const timeoutMs = (entry.timeout ?? defaultTimeoutSec) * 1000;
		const child = execFile("bash", ["-c", entry.command], { timeout: timeoutMs, env: process.env, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
			if (error) {
				const killed = (error as NodeJS.ErrnoException & { killed?: boolean }).killed ?? false;
				// When process exits non-zero, error.code is the exit code (number).
				// When killed by timeout, error.code is null or 'ETIMEDOUT'.
				const code = (error as NodeJS.ErrnoException & { code?: unknown }).code;
				const exitCode = typeof code === "number" ? code : killed ? 1 : 1;
				resolve({ exitCode, stdout, stderr, timedOut: killed });
			} else {
				resolve({ exitCode: 0, stdout, stderr: stderr ?? "", timedOut: false });
			}
		});
		child.stdin?.write(stdinJson);
		child.stdin?.end();
	});
}

function runHookAsync(entry: HookEntry, stdinJson: string, notifyFn: (msg: string, level: "error" | "warning") => void, defaultTimeoutSec = 60): void {
	runHook(entry, stdinJson, defaultTimeoutSec)
		.then((result) => {
			if (result.exitCode === 2 && result.stderr.trim()) {
				notifyFn(result.stderr.trim(), "warning");
			} else if (result.exitCode !== 0) {
				notifyFn(`Hook error (${entry.command.split("/").at(-1)}): ${result.stderr || "non-zero exit"}`, "error");
			}
		})
		.catch(() => {
			// Stale extension context after session end — ignore silently
		});
}

// ---------------------------------------------------------------------------
// Common stdin builder
// ---------------------------------------------------------------------------

function baseStdin(hookEventName: string, ctx: ExtensionContext): Record<string, unknown> {
	return {
		session_id: ctx.sessionManager.getSessionId(),
		cwd: ctx.cwd,
		hook_event_name: hookEventName,
	};
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function (pi: ExtensionAPI): void {
	// --- SessionStart → SessionStart or SubagentStart ---
	pi.on("session_start", async (event: SessionStartEvent, ctx: ExtensionContext) => {
		if (event.reason === "reload") return;
		loadConfig(ctx.cwd);

		// Pi has no built-in subagent detection on session_start; treat all as SessionStart
		const hookName = "SessionStart";
		const stdin = JSON.stringify({
			...baseStdin(hookName, ctx),
			source: event.reason,
		});

		for (const group of resolvedConfig()[hookName] ?? []) {
			for (const entry of group.hooks) {
				if (entry.async) {
					runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
					continue;
				}
				const result = await runHook(entry, stdin);
				if (result.exitCode === 0 && result.stdout.trim()) {
					ctx.ui.notify(result.stdout.trim(), "info");
				} else if (result.timedOut) {
					ctx.ui.notify(`Session hook timed out: ${entry.command.split("/").at(-1)}`, "error");
				} else if (result.exitCode !== 0) {
					ctx.ui.notify(`Session hook error: ${result.stderr || "non-zero exit"}`, "error");
				}
			}
		}
	});

	// --- agent_start → SubagentStart ---
	// Fires for every agent loop start; in a subagent session this covers SubagentStart
	pi.on("agent_start", async (_event: AgentStartEvent, ctx: ExtensionContext) => {
		const stdin = JSON.stringify(baseStdin("SubagentStart", ctx));
		for (const group of resolvedConfig().SubagentStart ?? []) {
			for (const entry of group.hooks) {
				runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
			}
		}
	});

	// --- session_shutdown → SessionEnd or SubagentStop ---
	pi.on("session_shutdown", async (event: SessionShutdownEvent, ctx: ExtensionContext) => {
		const hookName = "SessionEnd";
		const stdin = JSON.stringify({
			...baseStdin(hookName, ctx),
			end_reason: event.reason,
		});
		for (const group of resolvedConfig()[hookName] ?? []) {
			for (const entry of group.hooks) {
				runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
			}
		}
	});

	// --- agent_end → Stop ---
	pi.on("agent_end", async (_event: AgentEndEvent, ctx: ExtensionContext) => {
		const stdin = JSON.stringify(baseStdin("Stop", ctx));
		for (const group of resolvedConfig().Stop ?? []) {
			for (const entry of group.hooks) {
				if (entry.async) {
					runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
					continue;
				}
				const result = await runHook(entry, stdin);
				if (result.exitCode === 2 && result.stderr.trim()) {
					// Simulate CC's "prevent stop": inject reason as a continuation prompt
					try {
						await ctx.sendUserMessage(result.stderr.trim(), { triggerTurn: true });
					} catch {
						ctx.ui.notify(result.stderr.trim(), "warning");
					}
				} else if (result.exitCode !== 0) {
					ctx.ui.notify(`Stop hook error: ${result.stderr}`, "error");
				}
			}
		}
		// Note: notify.ts handles the Notification/terminal-notifier equivalent
	});

	// --- session_before_compact → PreCompact ---
	pi.on("session_before_compact", async (_event: SessionBeforeCompactEvent, ctx: ExtensionContext): Promise<SessionBeforeCompactResult | undefined> => {
		const stdin = JSON.stringify({
			...baseStdin("PreCompact", ctx),
			trigger: "unknown", // Pi doesn't expose auto vs manual here
		});
		for (const group of resolvedConfig().PreCompact ?? []) {
			for (const entry of group.hooks) {
				const result = await runHook(entry, stdin);
				if (result.exitCode === 2) return { cancel: true };
				if (result.exitCode !== 0) ctx.ui.notify(`PreCompact hook error: ${result.stderr}`, "error");
			}
		}
		return undefined;
	});

	// --- session_compact → PostCompact ---
	pi.on("session_compact", async (event: SessionCompactEvent, ctx: ExtensionContext) => {
		const stdin = JSON.stringify({
			...baseStdin("PostCompact", ctx),
			trigger: event.fromExtension ? "manual" : "auto",
		});
		for (const group of resolvedConfig().PostCompact ?? []) {
			for (const entry of group.hooks) {
				if (entry.async) {
					runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
					continue;
				}
				const result = await runHook(entry, stdin);
				if (result.exitCode !== 0) ctx.ui.notify(`PostCompact hook error: ${result.stderr}`, "error");
			}
		}
	});

	// --- before_agent_start → UserPromptSubmit ---
	pi.on("before_agent_start", async (event: BeforeAgentStartEvent, ctx: ExtensionContext): Promise<BeforeAgentStartEventResult | undefined> => {
		const stdin = JSON.stringify({
			...baseStdin("UserPromptSubmit", ctx),
			prompt: event.prompt,
		});

		let injected = "";
		for (const group of resolvedConfig().UserPromptSubmit ?? []) {
			for (const entry of group.hooks) {
				const result = await runHook(entry, stdin, 15);
				if (result.exitCode === 2 && result.stderr.trim()) {
					// Hook tried to block — surface as injected context (Pi can't block before_agent_start)
					injected += result.stderr.trim() + "\n";
				} else if (result.exitCode === 0 && result.stdout.trim()) {
					// Stdout (e.g. skill-enforcer's "→ Consider skills: ...") injected as LLM context
					injected += result.stdout.trim() + "\n";
				} else if (result.exitCode !== 0) {
					ctx.ui.notify(`Prompt hook error: ${result.stderr}`, "error");
				}
			}
		}

		if (!injected.trim()) return undefined;
		const text = injected.trim();
		return {
			message: {
				customType: "hook-context",
				content: [{ type: "text", text }],
				display: text,
			},
		};
	});

	// --- tool_call → PreToolUse (blocking) ---
	pi.on("tool_call", async (event: ToolCallEvent, ctx: ExtensionContext): Promise<ToolCallEventResult | undefined> => {
		const ccName = toCcToolName(event.toolName);
		const stdin = JSON.stringify({
			...baseStdin("PreToolUse", ctx),
			tool_name: ccName,
			tool_input: event.input,
			tool_use_id: event.toolCallId,
		});

		for (const group of matchingGroups(resolvedConfig().PreToolUse ?? [], ccName)) {
			for (const entry of group.hooks) {
				const result = await runHook(entry, stdin, 10);
				if (result.exitCode === 2) {
					return { block: true, reason: result.stderr.trim() || "Blocked by hook" };
				}
				if (result.exitCode !== 0) {
					ctx.ui.notify(`Pre-tool hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				}
			}
		}
		return undefined;
	});

	// --- tool_result → PostToolUse / PostToolUseFailure (LLM feedback loop) ---
	pi.on("tool_result", async (event: ToolResultEvent, ctx: ExtensionContext): Promise<ToolResultEventResult | undefined> => {
		const ccName = toCcToolName(event.toolName);
		const hookName = event.isError ? "PostToolUseFailure" : "PostToolUse";
		const stdin = JSON.stringify({
			...baseStdin(hookName, ctx),
			tool_name: ccName,
			tool_input: event.input,
			tool_use_id: event.toolCallId,
			...(event.isError
				? { error: "tool execution failed" }
				: {
						tool_response: event.content
							.filter((c): c is { type: "text"; text: string } => c.type === "text")
							.map((c) => c.text)
							.join("\n"),
					}),
		});

		const groups = matchingGroups(resolvedConfig()[hookName] ?? [], ccName);
		const feedbackLines: string[] = [];

		for (const group of groups) {
			for (const entry of group.hooks) {
				if (entry.async) {
					runHookAsync(entry, stdin, (msg, lvl) => ctx.ui.notify(msg, lvl), entry.timeout ?? 120);
					continue;
				}
				const result = await runHook(entry, stdin, entry.timeout ?? 60);
				if (result.exitCode === 2 && result.stderr.trim()) {
					// Feedback loop: append stderr to tool result content so LLM sees and fixes issues
					feedbackLines.push(result.stderr.trim());
				} else if (result.exitCode !== 0) {
					ctx.ui.notify(`Post-tool hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				}
			}
		}

		if (feedbackLines.length === 0) return undefined;
		const feedbackText = "⚠️ Hook output:\n" + feedbackLines.join("\n---\n");
		return {
			content: [...event.content, { type: "text", text: feedbackText }],
		};
	});
}
