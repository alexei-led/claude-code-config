/**
 * Hook Runner — maps Pi runtime events and synthetic extension events to CC-compatible hooks.
 *
 * Hook defaults are loaded from bundled `hooks.json` (deployed with this extension), then
 * merged with user/project overrides from Pi settings/hooks files.
 * Extensions can invoke synthetic events over cc-hooks:invoke (PermissionRequest, ExitPlanMode, etc).
 */

import type {
	AgentEndEvent,
	AgentStartEvent,
	BeforeAgentStartEvent,
	BeforeAgentStartEventResult,
	ExtensionAPI,
	ExtensionContext,
	InputEvent,
	InputEventResult,
	SessionBeforeCompactEvent,
	SessionCompactEvent,
	SessionShutdownEvent,
	SessionStartEvent,
	ToolCallEvent,
	ToolCallEventResult,
	ToolResultEvent,
	TurnEndEvent,
} from "@earendil-works/pi-coding-agent";
import { execFile } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
	HOOK_RUNNER_INVOKE_CHANNEL,
	SYNTHETIC_HOOK_EVENT_NAMES,
	type SyntheticHookInvocationRequest,
	type SyntheticHookInvocationResult,
} from "./hook-bridge.js";

// ---------------------------------------------------------------------------
// Path resolution — works regardless of where Pi cloned the package
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// dist/pi/extensions/hook-runner.ts → ../hooks → dist/pi/hooks
const HOOKS_DIR = join(__dirname, "..", "hooks");
const BUNDLED_HOOKS_CONFIG_PATH = join(__dirname, "hooks.json");
const PI_HOOKS_DIR_PLACEHOLDER = "${PI_HOOKS_DIR}";

function agentDir(): string {
	return process.env.PI_CODING_AGENT_DIR || join(homedir(), ".pi", "agent");
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

const CORE_HOOK_EVENT_NAMES = [
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

const HOOK_EVENT_NAMES = [...SYNTHETIC_HOOK_EVENT_NAMES, ...CORE_HOOK_EVENT_NAMES] as const;

type HookEventName = (typeof HOOK_EVENT_NAMES)[number];

function isHookEventName(value: unknown): value is HookEventName {
	return typeof value === "string" && (HOOK_EVENT_NAMES as readonly string[]).includes(value);
}

type HookSource = "bundled" | "global" | "project";

interface HookEntry {
	type: "command";
	command: string;
	timeout?: number; // seconds; default varies by hook family
	async?: boolean; // fire-and-forget
	// Internal-only metadata, attached during loadConfig. Never persisted.
	_source?: HookSource;
	_disabled?: boolean;
}

interface HookGroup {
	matcher?: string; // regex matched against CC-style tool name; undefined = match all
	hooks: HookEntry[];
}

interface HooksConfig {
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
	[key: string]: HookGroup[] | undefined; // extensible for user configs
}

interface HookRunResult {
	exitCode: number;
	stdout: string;
	stderr: string;
	timedOut: boolean;
}

interface ParsedPreToolUseOutput {
	decision?: "allow" | "ask" | "deny" | "defer";
	reason?: string;
	updatedInput?: Record<string, unknown>;
	additionalContext?: string;
}

interface ParsedPermissionRequestOutput {
	behavior?: "allow" | "deny";
	message?: string;
	interrupt?: boolean;
	updatedInput?: Record<string, unknown>;
}

interface ParsedPermissionDeniedOutput {
	retry?: boolean;
}

interface ParsedDecisionOutput {
	block?: boolean;
	reason?: string;
	additionalContext?: string;
}

// ---------------------------------------------------------------------------
// Tool name normalization: Pi lowercase → CC names
// ---------------------------------------------------------------------------

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
};

function toCcToolName(piName: string): string {
	return TOOL_NAME_MAP[piName.toLowerCase()] ?? (piName === piName.toLowerCase() ? piName.charAt(0).toUpperCase() + piName.slice(1) : piName);
}

// ---------------------------------------------------------------------------
// Config loading (lazy — on first session_start)
// ---------------------------------------------------------------------------

interface HookRunnerOptions {
	disableBundledHooks?: boolean;
	disabledHooks?: string[]; // command basenames to skip
}

let _config: HooksConfig | null = null;
let _configRaw: HooksConfig | null = null; // pre-filter view for /hooks summary
let _configLoadedForCwd = "";
let _ifWarningShown = false;
let _lastForcedReloadMs = 0;
const FORCED_RELOAD_DEBOUNCE_MS = 500;

function mergeHooks(base: HooksConfig, user: HooksConfig): void {
	for (const [key, groups] of Object.entries(user)) {
		if (!groups) continue;
		const existing = base[key];
		base[key] = existing ? [...existing, ...groups] : [...groups];
	}
}

function normalizeHookConfig(raw: unknown): HooksConfig {
	if (!isRecord(raw)) return {};
	const normalized: HooksConfig = {};
	for (const [key, groups] of Object.entries(raw)) {
		if (key === "hookRunner") continue;
		if (!Array.isArray(groups)) continue;
		const validGroups: HookGroup[] = [];
		for (const group of groups) {
			if (!isRecord(group)) continue;
			if (!Array.isArray(group.hooks)) continue;
			const validEntries = group.hooks.filter((e): e is HookEntry => isRecord(e) && typeof e.command === "string");
			if (validEntries.length === 0) continue;
			validGroups.push({ matcher: typeof group.matcher === "string" ? group.matcher : undefined, hooks: validEntries });
		}
		if (validGroups.length > 0) normalized[key] = validGroups;
	}
	return normalized;
}

function resolveBundledHookPaths(config: HooksConfig): HooksConfig {
	const resolved: HooksConfig = {};
	for (const [eventName, groups] of Object.entries(config)) {
		if (!groups) continue;
		resolved[eventName] = groups.map((group) => ({
			matcher: group.matcher,
			hooks: group.hooks.map((entry) => ({
				...entry,
				command: entry.command.replaceAll(PI_HOOKS_DIR_PLACEHOLDER, HOOKS_DIR),
			})),
		}));
	}
	return resolved;
}

function extractHookRunnerOptions(parsed: unknown): HookRunnerOptions {
	if (!isRecord(parsed)) return {};
	const raw = parsed.hookRunner;
	if (!isRecord(raw)) return {};
	const opts: HookRunnerOptions = {
		disableBundledHooks: raw.disableBundledHooks === true,
	};
	if (Array.isArray(raw.disabledHooks)) {
		opts.disabledHooks = raw.disabledHooks.filter((v): v is string => typeof v === "string");
	}
	return opts;
}

function tagEntries(config: HooksConfig, source: HookSource): HooksConfig {
	const out: HooksConfig = {};
	for (const [eventName, groups] of Object.entries(config)) {
		if (!groups) continue;
		out[eventName] = groups.map((group) => ({
			matcher: group.matcher,
			hooks: group.hooks.map((entry) => ({ ...entry, _source: source })),
		}));
	}
	return out;
}

function basename(commandPath: string): string {
	const trimmed = commandPath.trim().split(/\s+/)[0] ?? "";
	return trimmed.split("/").pop() ?? trimmed;
}

function applyDisabled(config: HooksConfig, disabled: Set<string>): void {
	if (disabled.size === 0) return;
	for (const groups of Object.values(config)) {
		if (!groups) continue;
		for (const group of groups) {
			for (const entry of group.hooks) {
				if (disabled.has(basename(entry.command))) {
					entry._disabled = true;
				}
			}
		}
	}
}

function filterEnabled(config: HooksConfig): HooksConfig {
	const out: HooksConfig = {};
	for (const [eventName, groups] of Object.entries(config)) {
		if (!groups) continue;
		const filteredGroups = groups
			.map((group) => ({
				matcher: group.matcher,
				hooks: group.hooks.filter((entry) => entry._disabled !== true),
			}))
			.filter((group) => group.hooks.length > 0);
		if (filteredGroups.length > 0) {
			out[eventName] = filteredGroups;
		}
	}
	return out;
}

function extractHooksConfig(parsed: unknown, configPath: string): HooksConfig {
	if (!isRecord(parsed)) return {};
	const nestedHooks = parsed.hooks;
	if (isRecord(nestedHooks)) {
		return normalizeHookConfig(nestedHooks);
	}
	if (configPath.endsWith("hooks.json")) {
		return normalizeHookConfig(parsed);
	}
	return {};
}

function loadBundledHooksConfig(): HooksConfig {
	try {
		const raw = readFileSync(BUNDLED_HOOKS_CONFIG_PATH, "utf-8");
		const parsed = JSON.parse(raw) as unknown;
		const bundled = extractHooksConfig(parsed, BUNDLED_HOOKS_CONFIG_PATH);
		return resolveBundledHookPaths(bundled);
	} catch {
		return {};
	}
}

function hasUnsupportedIfPredicate(config: HooksConfig): boolean {
	return Object.values(config)
		.flat()
		.flatMap((g) => g?.hooks ?? [])
		.some((h) => "if" in h);
}

function loadConfig(cwd: string, force = false): void {
	if (!force && _config && _configLoadedForCwd === cwd) return;
	_configLoadedForCwd = cwd;

	const globalAgentDir = agentDir();
	const configPaths: Array<{ path: string; source: HookSource }> = [
		{ path: join(globalAgentDir, "settings.json"), source: "global" },
		{ path: join(globalAgentDir, "hooks.json"), source: "global" },
		{ path: join(cwd, ".pi", "settings.json"), source: "project" },
		{ path: join(cwd, ".pi", "hooks.json"), source: "project" },
	];

	let disableBundledHooks = false;
	const disabledNames = new Set<string>();
	const hookConfigs: Array<{ config: HooksConfig; source: HookSource }> = [];

	for (const { path: configPath, source } of configPaths) {
		try {
			const raw = readFileSync(configPath, "utf-8");
			const parsed = JSON.parse(raw) as unknown;
			const options = extractHookRunnerOptions(parsed);
			if (typeof options.disableBundledHooks === "boolean") {
				disableBundledHooks = options.disableBundledHooks;
			}
			if (options.disabledHooks) {
				for (const name of options.disabledHooks) disabledNames.add(name);
			}
			const hooksConfig = extractHooksConfig(parsed, configPath);
			if (Object.keys(hooksConfig).length > 0) {
				hookConfigs.push({ config: hooksConfig, source });
			}
		} catch {
			// File absent or malformed: silently skip
		}
	}

	const base = disableBundledHooks ? {} : tagEntries(loadBundledHooksConfig(), "bundled");
	for (const { config, source } of hookConfigs) {
		mergeHooks(base, tagEntries(config, source));
		if (_ifWarningShown) continue;
		if (hasUnsupportedIfPredicate(config)) {
			_ifWarningShown = true;
			console.warn("[hook-runner] 'if' predicate in hooks config is not supported in v1; use 'matcher' instead");
		}
	}

	applyDisabled(base, disabledNames);
	_configRaw = base;
	_config = filterEnabled(base);
}

function resolvedConfig(): HooksConfig {
	return _config ?? loadBundledHooksConfig();
}

export function _resetForTesting(): void {
	_config = null;
	_configRaw = null;
	_configLoadedForCwd = "";
	_ifWarningShown = false;
}

export { toCcToolName, matcherMatches, matchingGroups };

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
// Hook output parsing
// ---------------------------------------------------------------------------

function isRecord(value: unknown): value is Record<string, unknown> {
	return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function parseJsonObject(raw: string): Record<string, unknown> | undefined {
	const trimmed = raw.trim();
	if (!trimmed) return undefined;
	try {
		const parsed = JSON.parse(trimmed) as unknown;
		if (!isRecord(parsed)) return undefined;
		return parsed;
	} catch {
		return undefined;
	}
}

function hookSpecificOutput(parsed: Record<string, unknown>, hookEventName: HookEventName): Record<string, unknown> | undefined {
	const raw = parsed.hookSpecificOutput;
	if (!raw || typeof raw !== "object" || Array.isArray(raw)) return undefined;
	const value = raw as Record<string, unknown>;
	const declared = value.hookEventName;
	if (typeof declared === "string" && declared !== hookEventName) {
		return undefined;
	}
	return value;
}

function parsePreToolUseOutput(stdout: string): ParsedPreToolUseOutput {
	const parsed = parseJsonObject(stdout);
	if (!parsed) return {};

	const hso = hookSpecificOutput(parsed, "PreToolUse") ?? parsed;
	const legacyDecision = typeof hso.decision === "string" ? hso.decision : typeof parsed.decision === "string" ? parsed.decision : undefined;
	let decision = typeof hso.permissionDecision === "string" ? hso.permissionDecision : legacyDecision;
	if (decision === "approve") decision = "allow";
	if (decision === "block") decision = "deny";
	if (decision && !["allow", "ask", "deny", "defer"].includes(decision)) {
		decision = undefined;
	}

	const reason =
		typeof hso.permissionDecisionReason === "string"
			? hso.permissionDecisionReason
			: typeof hso.reason === "string"
				? hso.reason
				: typeof parsed.reason === "string"
					? parsed.reason
					: undefined;

	const updatedInputRaw = hso.updatedInput;
	const updatedInput =
		updatedInputRaw && typeof updatedInputRaw === "object" && !Array.isArray(updatedInputRaw) ? (updatedInputRaw as Record<string, unknown>) : undefined;

	const additionalContext =
		typeof hso.additionalContext === "string" ? hso.additionalContext : typeof parsed.additionalContext === "string" ? parsed.additionalContext : undefined;

	return {
		decision: decision as ParsedPreToolUseOutput["decision"],
		reason,
		updatedInput,
		additionalContext,
	};
}

function parsePermissionRequestOutput(stdout: string): ParsedPermissionRequestOutput {
	const parsed = parseJsonObject(stdout);
	if (!parsed) return {};
	const hso = hookSpecificOutput(parsed, "PermissionRequest");
	if (!hso) return {};
	const rawDecision = hso.decision;
	if (!rawDecision || typeof rawDecision !== "object" || Array.isArray(rawDecision)) {
		return {};
	}
	const decision = rawDecision as Record<string, unknown>;
	const behavior = decision.behavior;
	if (behavior !== "allow" && behavior !== "deny") {
		return {};
	}
	const updatedInputRaw = decision.updatedInput;
	const updatedInput =
		updatedInputRaw && typeof updatedInputRaw === "object" && !Array.isArray(updatedInputRaw) ? (updatedInputRaw as Record<string, unknown>) : undefined;
	return {
		behavior,
		message: typeof decision.message === "string" ? decision.message : undefined,
		interrupt: typeof decision.interrupt === "boolean" ? decision.interrupt : undefined,
		updatedInput,
	};
}

function parsePermissionDeniedOutput(stdout: string): ParsedPermissionDeniedOutput {
	const parsed = parseJsonObject(stdout);
	if (!parsed) return {};
	const hso = hookSpecificOutput(parsed, "PermissionDenied");
	if (!hso) return {};
	return { retry: hso.retry === true };
}

function parseDecisionOutput(stdout: string, hookEventName: HookEventName): ParsedDecisionOutput {
	const parsed = parseJsonObject(stdout);
	if (!parsed) return {};
	const hso = hookSpecificOutput(parsed, hookEventName) ?? parsed;
	const decision = typeof hso.decision === "string" ? hso.decision : typeof parsed.decision === "string" ? parsed.decision : undefined;
	const continueField = typeof hso.continue === "boolean" ? hso.continue : typeof parsed.continue === "boolean" ? parsed.continue : undefined;
	const reason =
		typeof hso.reason === "string"
			? hso.reason
			: typeof parsed.reason === "string"
				? parsed.reason
				: typeof hso.stopReason === "string"
					? hso.stopReason
					: typeof parsed.stopReason === "string"
						? parsed.stopReason
						: undefined;
	const additionalContext =
		typeof hso.additionalContext === "string" ? hso.additionalContext : typeof parsed.additionalContext === "string" ? parsed.additionalContext : undefined;
	return {
		block: decision === "block" || continueField === false,
		reason,
		additionalContext,
	};
}

function replaceInput(target: Record<string, unknown>, replacement: Record<string, unknown>): void {
	for (const key of Object.keys(target)) {
		delete target[key];
	}
	Object.assign(target, replacement);
}

function serializeToolContent(content: Array<{ type: string; text?: string; source?: unknown; mediaType?: string }>): string {
	const parts: string[] = [];
	for (const block of content) {
		if (block.type === "text" && typeof block.text === "string") {
			parts.push(block.text);
			continue;
		}
		if (block.type === "image") {
			parts.push("[image]");
		}
	}
	return parts.join("\n");
}

function parseSlashCommand(text: string): { commandName: string; commandArgs: string; prompt: string } | undefined {
	const trimmed = text.trim();
	if (!trimmed.startsWith("/") || trimmed.startsWith("//")) return undefined;
	const withoutSlash = trimmed.slice(1).trim();
	if (!withoutSlash) return undefined;
	const [commandName, ...rest] = withoutSlash.split(/\s+/);
	if (!commandName) return undefined;
	return {
		commandName,
		commandArgs: rest.join(" "),
		prompt: trimmed,
	};
}

function sendHookMessageToAgent(pi: ExtensionAPI, ctx: ExtensionContext, text: string): void {
	const payload = text.trim();
	if (!payload) return;
	try {
		if (ctx.isIdle()) {
			pi.sendUserMessage(payload);
			return;
		}
		pi.sendUserMessage(payload, { deliverAs: "steer" });
	} catch {
		try {
			pi.sendUserMessage(payload, { deliverAs: "followUp" });
		} catch {
			ctx.ui.notify(payload, "warning");
		}
	}
}

function discoverInstructionFiles(cwd: string): Array<{ file_path: string; memory_type: string; load_reason: string }> {
	const files: Array<{ file_path: string; memory_type: string; load_reason: string }> = [];
	const seen = new Set<string>();
	const add = (filePath: string, memoryType: string, loadReason = "session_start") => {
		if (!existsSync(filePath)) return;
		if (seen.has(filePath)) return;
		seen.add(filePath);
		files.push({ file_path: filePath, memory_type: memoryType, load_reason: loadReason });
	};

	const userAgents = join(agentDir(), "AGENTS.md");
	add(userAgents, "User");

	let current = cwd;
	while (true) {
		add(join(current, "AGENTS.md"), "Project");
		add(join(current, "CLAUDE.md"), "Project");
		const rulesDir = join(current, ".claude", "rules");
		if (existsSync(rulesDir)) {
			try {
				for (const file of readdirSync(rulesDir)) {
					if (file.endsWith(".md")) {
						add(join(rulesDir, file), "Project", "path_glob_match");
					}
				}
			} catch {
				// ignore unreadable rules dir
			}
		}
		const parent = dirname(current);
		if (parent === current) break;
		current = parent;
	}

	return files;
}

function projectHooksConfigPath(cwd: string): string {
	return join(cwd, ".pi", "hooks.json");
}

function globalHooksConfigPath(): string {
	return join(agentDir(), "hooks.json");
}

function readHookRunnerOptions(path: string): HookRunnerOptions {
	try {
		const raw = readFileSync(path, "utf-8");
		const parsed = JSON.parse(raw) as unknown;
		return extractHookRunnerOptions(parsed);
	} catch {
		return {};
	}
}

function readProjectHookRunnerOptions(cwd: string): HookRunnerOptions {
	return readHookRunnerOptions(projectHooksConfigPath(cwd));
}

function writeHooksConfig(path: string, parsed: Record<string, unknown>): void {
	mkdirSync(dirname(path), { recursive: true });
	writeFileSync(path, JSON.stringify(parsed, null, 2) + "\n", "utf-8");
}

function rawConfig(): HooksConfig {
	return _configRaw ?? loadBundledHooksConfig();
}

function hooksSummary(config: HooksConfig): string {
	const lines: string[] = [];
	const events = Object.keys(config).sort();
	for (const eventName of events) {
		const groups = config[eventName];
		if (!groups || groups.length === 0) continue;
		lines.push(`${eventName}:`);
		for (const group of groups) {
			const matcher = group.matcher ? `[${group.matcher}]` : "[*]";
			for (const entry of group.hooks) {
				const source = entry._source ?? "?";
				const status = entry._disabled ? " (disabled)" : "";
				const flags = entry.async ? " async" : "";
				lines.push(`  ${matcher} ${basename(entry.command)} (${source})${flags}${status}`);
			}
		}
	}
	if (lines.length === 0) return "No hooks configured.";
	return lines.join("\n");
}

function listAllHookNames(config: HooksConfig): { name: string; disabled: boolean; source: HookSource | "?" }[] {
	const seen = new Map<string, { name: string; disabled: boolean; source: HookSource | "?" }>();
	for (const groups of Object.values(config)) {
		if (!groups) continue;
		for (const group of groups) {
			for (const entry of group.hooks) {
				const name = basename(entry.command);
				if (!name) continue;
				const existing = seen.get(name);
				if (!existing) {
					seen.set(name, { name, disabled: entry._disabled === true, source: entry._source ?? "?" });
				} else if (entry._disabled) {
					existing.disabled = true;
				}
			}
		}
	}
	return [...seen.values()].sort((a, b) => a.name.localeCompare(b.name));
}

// ---------------------------------------------------------------------------
// Hook execution
// ---------------------------------------------------------------------------

function runHook(entry: HookEntry, stdinJson: string, defaultTimeoutSec = 30): Promise<HookRunResult> {
	return new Promise((resolve) => {
		const timeoutMs = (entry.timeout ?? defaultTimeoutSec) * 1000;
		const child = execFile("bash", ["-c", entry.command], { timeout: timeoutMs, env: process.env, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
			if (error) {
				const err = error as Error & { killed?: boolean; code?: unknown };
				const killed = err.killed ?? false;
				// code is a number when process exits non-zero; string/null when killed by timeout
				const exitCode = typeof err.code === "number" ? err.code : 1;
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
// Common stdin builders
// ---------------------------------------------------------------------------

function baseStdin(hookEventName: HookEventName, ctx: ExtensionContext): Record<string, unknown> {
	return {
		session_id: ctx.sessionManager.getSessionId(),
		cwd: ctx.cwd,
		hook_event_name: hookEventName,
	};
}

function baseStdinFromRecord(hookEventName: HookEventName, stdin: Record<string, unknown>): Record<string, unknown> {
	return {
		session_id: stdin.session_id,
		cwd: stdin.cwd,
		hook_event_name: hookEventName,
	};
}

// ---------------------------------------------------------------------------
// Core dispatchers
// ---------------------------------------------------------------------------

async function runPreToolUseGroups(
	groups: HookGroup[],
	ccToolName: string,
	stdin: string,
	ctx?: ExtensionContext,
	defaultTimeout = 10,
): Promise<SyntheticHookInvocationResult> {
	let selectedDecision: "allow" | "ask" | "deny" | "defer" | undefined;
	let selectedReason = "";
	let selectedRank = 0;
	let updatedInput: Record<string, unknown> | undefined;
	const extraContexts: string[] = [];

	const rank: Record<"allow" | "ask" | "defer" | "deny", number> = {
		allow: 1,
		ask: 2,
		defer: 3,
		deny: 4,
	};

	for (const group of matchingGroups(groups, ccToolName)) {
		for (const entry of group.hooks) {
			const result = await runHook(entry, stdin, defaultTimeout);
			if (result.timedOut) {
				return {
					blocked: true,
					reason: result.stderr.trim() || `Hook timed out: ${entry.command.split("/").at(-1)}`,
					decision: "deny",
				};
			}
			if (result.exitCode === 2) {
				return {
					blocked: true,
					reason: result.stderr.trim() || "Blocked by hook",
					decision: "deny",
				};
			}
			if (result.exitCode !== 0) {
				ctx?.ui.notify(`Pre-tool hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				continue;
			}
			const parsed = parsePreToolUseOutput(result.stdout);
			if (parsed.updatedInput) {
				updatedInput = parsed.updatedInput;
			}
			if (parsed.additionalContext) {
				extraContexts.push(parsed.additionalContext);
			}
			if (parsed.decision) {
				const currentRank = rank[parsed.decision];
				if (currentRank > selectedRank) {
					selectedRank = currentRank;
					selectedDecision = parsed.decision;
					selectedReason = parsed.reason ?? selectedReason;
				}
			}
		}
	}

	if (selectedDecision === "deny") {
		return {
			blocked: true,
			reason: selectedReason || "Blocked by hook",
			decision: "deny",
			updatedInput,
			additionalContext: extraContexts.join("\n").trim() || undefined,
		};
	}
	if (selectedDecision === "ask") {
		return {
			blocked: true,
			reason: selectedReason || "Blocked by hook: confirmation required (decision=ask)",
			decision: "ask",
			updatedInput,
			additionalContext: extraContexts.join("\n").trim() || undefined,
		};
	}
	if (selectedDecision === "defer") {
		return {
			blocked: true,
			reason: selectedReason || "Deferred by hook (unsupported in interactive Pi)",
			decision: "defer",
			updatedInput,
			additionalContext: extraContexts.join("\n").trim() || undefined,
		};
	}

	return {
		blocked: false,
		reason: selectedReason || undefined,
		decision: selectedDecision,
		updatedInput,
		additionalContext: extraContexts.join("\n").trim() || undefined,
	};
}

async function runPermissionRequestGroups(
	groups: HookGroup[],
	ccToolName: string,
	stdin: string,
	ctx?: ExtensionContext,
	defaultTimeout = 10,
): Promise<SyntheticHookInvocationResult> {
	for (const group of matchingGroups(groups, ccToolName)) {
		for (const entry of group.hooks) {
			const result = await runHook(entry, stdin, defaultTimeout);
			if (result.exitCode === 2) {
				return { blocked: true, reason: result.stderr.trim() || "Permission denied by hook", behavior: "deny" };
			}
			if (result.exitCode !== 0) {
				ctx?.ui.notify(`PermissionRequest hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				continue;
			}
			const parsed = parsePermissionRequestOutput(result.stdout);
			if (parsed.behavior === "deny") {
				return {
					blocked: true,
					reason: parsed.message || "Permission denied by hook",
					behavior: "deny",
					interrupt: parsed.interrupt,
				};
			}
			if (parsed.behavior === "allow") {
				return {
					blocked: false,
					behavior: "allow",
					updatedInput: parsed.updatedInput,
				};
			}
		}
	}
	return { blocked: false };
}

async function runPermissionDeniedGroups(
	groups: HookGroup[],
	ccToolName: string,
	stdin: string,
	ctx?: ExtensionContext,
): Promise<SyntheticHookInvocationResult> {
	let retry = false;
	for (const group of matchingGroups(groups, ccToolName)) {
		for (const entry of group.hooks) {
			const result = await runHook(entry, stdin, 10);
			if (result.exitCode !== 0) {
				ctx?.ui.notify(`PermissionDenied hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				continue;
			}
			const parsed = parsePermissionDeniedOutput(result.stdout);
			if (parsed.retry) retry = true;
		}
	}
	return { retry };
}

const NON_BLOCKING_HOOK_EVENTS = new Set<HookEventName>([
	"SessionStart",
	"Setup",
	"SessionEnd",
	"SubagentStart",
	"Notification",
	"PostCompact",
	"StopFailure",
	"InstructionsLoaded",
	"CwdChanged",
	"FileChanged",
	"WorktreeRemove",
]);

async function runDecisionHooks(
	hookName: HookEventName,
	groups: HookGroup[],
	stdin: string,
	ctx?: ExtensionContext,
): Promise<{ blocked: boolean; reason?: string; additionalContext?: string }> {
	let blocked = false;
	let blockReason = "";
	const contexts: string[] = [];
	for (const group of groups) {
		for (const entry of group.hooks) {
			const result = await runHook(entry, stdin, 15);
			if (result.exitCode === 2 && result.stderr.trim()) {
				blocked = true;
				blockReason = result.stderr.trim();
				continue;
			}
			if (result.exitCode !== 0) {
				ctx?.ui.notify(`${hookName} hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
				continue;
			}
			const parsed = parseDecisionOutput(result.stdout, hookName);
			if (parsed.block) {
				blocked = true;
				blockReason = parsed.reason || blockReason || `${hookName} blocked by hook`;
			}
			if (parsed.additionalContext) {
				contexts.push(parsed.additionalContext);
			} else if (result.stdout.trim() && !parseJsonObject(result.stdout)) {
				// Non-JSON stdout acts as extra context for events like UserPromptExpansion
				contexts.push(result.stdout.trim());
			}
		}
	}
	return {
		blocked,
		reason: blockReason || undefined,
		additionalContext: contexts.join("\n").trim() || undefined,
	};
}

// ---------------------------------------------------------------------------
// Main export
// ---------------------------------------------------------------------------

export default function (pi: ExtensionAPI): void {
	let pendingPromptExpansionContext = "";
	let lastHookCwd: string | undefined;
	const toolInputByCallId = new Map<string, Record<string, unknown>>();

	pi.registerCommand("hooks", {
		description: "Manage hook-runner config (project and global hooks.json)",
		handler: async (_args, ctx) => {
			if (!ctx.hasUI) {
				ctx.ui.notify("Hooks UI is only available in interactive mode.", "warning");
				return;
			}
			loadConfig(ctx.cwd);
			const options = readProjectHookRunnerOptions(ctx.cwd);
			const disableBundled = options.disableBundledHooks === true;
			const choice = await ctx.ui.select("Hook runner", [
				"Show active hooks",
				"Toggle individual hook",
				disableBundled ? "Enable bundled hooks (project)" : "Disable bundled hooks (project)",
				"Edit project hooks (.pi/hooks.json)",
				"Edit global hooks (~/.pi/agent/hooks.json)",
			]);
			if (choice === "Show active hooks") {
				ctx.ui.notify(hooksSummary(rawConfig()), "info");
				return;
			}
			if (choice === "Toggle individual hook") {
				await toggleIndividualHook(ctx);
				return;
			}
			if (choice === "Edit project hooks (.pi/hooks.json)") {
				await editHooksFile(ctx, projectHooksConfigPath(ctx.cwd), "project");
				return;
			}
			if (choice === "Edit global hooks (~/.pi/agent/hooks.json)") {
				await editHooksFile(ctx, globalHooksConfigPath(), "global");
				return;
			}
			if (choice === "Disable bundled hooks (project)" || choice === "Enable bundled hooks (project)") {
				toggleBundledHooks(projectHooksConfigPath(ctx.cwd), choice.startsWith("Disable"));
				loadConfig(ctx.cwd, true);
				ctx.ui.notify(choice.startsWith("Disable") ? "Bundled hooks disabled in .pi/hooks.json" : "Bundled hooks enabled in .pi/hooks.json", "info");
			}
		},
	});

	async function toggleIndividualHook(ctx: ExtensionContext): Promise<void> {
		const names = listAllHookNames(rawConfig());
		if (names.length === 0) {
			ctx.ui.notify("No hooks to toggle.", "info");
			return;
		}
		const label = (e: { name: string; disabled: boolean; source: HookSource | "?" }) => `${e.disabled ? "[ ]" : "[x]"} ${e.name} (${e.source})`;
		const scope = await ctx.ui.select("Write toggle to:", ["Project (.pi/hooks.json)", "Global (~/.pi/agent/hooks.json)"]);
		if (!scope) return;
		const path = scope.startsWith("Project") ? projectHooksConfigPath(ctx.cwd) : globalHooksConfigPath();
		const picked = await ctx.ui.select("Toggle hook:", names.map(label));
		if (!picked) return;
		const idx = names.findIndex((e) => label(e) === picked);
		if (idx < 0) return;
		const target = names[idx];
		const scopeDisabled = readDisabledList(path).includes(target.name);
		const willDisable = !scopeDisabled;
		updateDisabledList(path, target.name, willDisable);
		loadConfig(ctx.cwd, true);
		ctx.ui.notify(`${willDisable ? "Disabled" : "Enabled"} ${target.name} (${scope.startsWith("Project") ? "project" : "global"})`, "info");
	}

	async function editHooksFile(ctx: ExtensionContext, path: string, scope: HookSource): Promise<void> {
		let initial = "{}\n";
		try {
			initial = readFileSync(path, "utf-8");
		} catch {
			// keep default
		}
		const edited = await ctx.ui.editor(`Edit ${scope} hooks (${path}):`, initial);
		if (!edited || !edited.trim()) return;
		try {
			const parsed = JSON.parse(edited) as unknown;
			if (!isRecord(parsed)) {
				ctx.ui.notify("hooks.json must be a JSON object.", "error");
				return;
			}
			writeHooksConfig(path, parsed);
			loadConfig(ctx.cwd, true);
			ctx.ui.notify(`Updated ${scope} hooks.json`, "info");
		} catch {
			ctx.ui.notify("Invalid JSON. Not saved.", "error");
		}
	}

	function toggleBundledHooks(path: string, disable: boolean): void {
		let parsed: Record<string, unknown> = {};
		try {
			const raw = readFileSync(path, "utf-8");
			const current = JSON.parse(raw) as unknown;
			if (isRecord(current)) parsed = current;
		} catch {
			// start from empty object
		}
		const hookRunner = isRecord(parsed.hookRunner) ? (parsed.hookRunner as Record<string, unknown>) : {};
		hookRunner.disableBundledHooks = disable;
		parsed.hookRunner = hookRunner;
		writeHooksConfig(path, parsed);
	}

	function readDisabledList(path: string): string[] {
		try {
			const raw = readFileSync(path, "utf-8");
			const parsed = JSON.parse(raw) as unknown;
			if (!isRecord(parsed)) return [];
			const hookRunner = parsed.hookRunner;
			if (!isRecord(hookRunner)) return [];
			if (!Array.isArray(hookRunner.disabledHooks)) return [];
			return hookRunner.disabledHooks.filter((v): v is string => typeof v === "string");
		} catch {
			return [];
		}
	}

	function updateDisabledList(path: string, name: string, disable: boolean): void {
		let parsed: Record<string, unknown> = {};
		try {
			const raw = readFileSync(path, "utf-8");
			const current = JSON.parse(raw) as unknown;
			if (isRecord(current)) parsed = current;
		} catch {
			// start from empty object
		}
		const hookRunner = isRecord(parsed.hookRunner) ? (parsed.hookRunner as Record<string, unknown>) : {};
		const current = Array.isArray(hookRunner.disabledHooks) ? hookRunner.disabledHooks.filter((v): v is string => typeof v === "string") : [];
		const next = disable ? [...new Set([...current, name])] : current.filter((n) => n !== name);
		hookRunner.disabledHooks = next;
		parsed.hookRunner = hookRunner;
		writeHooksConfig(path, parsed);
	}

	// --- extension-to-extension synthetic hook bridge ---
	pi.events.on(HOOK_RUNNER_INVOKE_CHANNEL, (raw) => {
		void (async () => {
			if (!isRecord(raw)) return;
			const req = raw as Partial<SyntheticHookInvocationRequest>;
			if (typeof req.onResult !== "function") return;
			if (!isRecord(req.stdin)) {
				req.onResult({ blocked: true, reason: "invalid synthetic hook payload" });
				return;
			}
			if (!isHookEventName(req.hookEventName)) {
				req.onResult({ blocked: true, reason: `unsupported synthetic hook event: ${String(req.hookEventName)}` });
				return;
			}

			const hookEventName = req.hookEventName;
			const cwd = typeof req.stdin.cwd === "string" ? req.stdin.cwd : process.cwd();
			let force = false;
			if (hookEventName === "ConfigChange") {
				const now = Date.now();
				if (now - _lastForcedReloadMs >= FORCED_RELOAD_DEBOUNCE_MS) {
					_lastForcedReloadMs = now;
					force = true;
				}
			}
			loadConfig(cwd, force);

			const withBase = {
				...baseStdinFromRecord(hookEventName, req.stdin),
				...req.stdin,
				hook_event_name: hookEventName,
			};

			if (hookEventName === "PreToolUse") {
				const ccToolName = typeof req.ccToolName === "string" ? req.ccToolName : typeof req.stdin.tool_name === "string" ? req.stdin.tool_name : "";
				const stdin = JSON.stringify({ ...withBase, tool_name: ccToolName });
				const result = await runPreToolUseGroups(resolvedConfig().PreToolUse ?? [], ccToolName, stdin, undefined, req.timeoutSec ?? 10);
				req.onResult(result);
				return;
			}

			if (hookEventName === "PermissionRequest") {
				const ccToolName = typeof req.ccToolName === "string" ? req.ccToolName : typeof req.stdin.tool_name === "string" ? req.stdin.tool_name : "";
				const stdin = JSON.stringify({ ...withBase, tool_name: ccToolName });
				const result = await runPermissionRequestGroups(resolvedConfig().PermissionRequest ?? [], ccToolName, stdin, undefined, req.timeoutSec ?? 10);
				req.onResult(result);
				return;
			}

			if (hookEventName === "PermissionDenied") {
				const ccToolName = typeof req.ccToolName === "string" ? req.ccToolName : typeof req.stdin.tool_name === "string" ? req.stdin.tool_name : "";
				const stdin = JSON.stringify({ ...withBase, tool_name: ccToolName });
				const result = await runPermissionDeniedGroups(resolvedConfig().PermissionDenied ?? [], ccToolName, stdin);
				req.onResult(result);
				return;
			}

			const stdin = JSON.stringify(withBase);
			const groups = resolvedConfig()[hookEventName] ?? [];
			const parsed = await runDecisionHooks(hookEventName, groups, stdin);
			const blocked = NON_BLOCKING_HOOK_EVENTS.has(hookEventName) ? false : parsed.blocked;
			req.onResult({ blocked, reason: parsed.reason, additionalContext: parsed.additionalContext });
		})();
	});

	// --- SessionStart → SessionStart (+ InstructionsLoaded snapshot) ---
	pi.on("session_start", async (event: SessionStartEvent, ctx: ExtensionContext) => {
		if (event.reason === "reload") return;
		loadConfig(ctx.cwd);
		lastHookCwd = ctx.cwd;

		const hookName: HookEventName = "SessionStart";
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

		const instructionsHookName: HookEventName = "InstructionsLoaded";
		for (const file of discoverInstructionFiles(ctx.cwd)) {
			const fileStdin = JSON.stringify({
				...baseStdin(instructionsHookName, ctx),
				file_path: file.file_path,
				memory_type: file.memory_type,
				load_reason: file.load_reason,
			});
			const groups = matchingGroups(resolvedConfig()[instructionsHookName] ?? [], file.load_reason);
			for (const group of groups) {
				for (const entry of group.hooks) {
					runHookAsync(entry, fileStdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
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

	// --- session_shutdown → SessionEnd ---
	pi.on("session_shutdown", async (event: SessionShutdownEvent, ctx: ExtensionContext) => {
		const hookName: HookEventName = "SessionEnd";
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

	// --- agent_end → Stop / StopFailure + Notification ---
	pi.on("agent_end", async (event: AgentEndEvent, ctx: ExtensionContext) => {
		const lastAssistant = [...event.messages].reverse().find((m) => m.role === "assistant") as
			| { role: "assistant"; stopReason?: string; errorMessage?: string; content?: Array<{ type: string; text?: string }> }
			| undefined;
		const isFailure = lastAssistant?.stopReason === "error";

		if (isFailure) {
			const hookName: HookEventName = "StopFailure";
			const lastText =
				lastAssistant?.errorMessage ||
				(lastAssistant?.content ?? [])
					.filter((p) => p.type === "text" && typeof p.text === "string")
					.map((p) => p.text)
					.join("\n");
			const failureStdin = JSON.stringify({
				...baseStdin(hookName, ctx),
				error: "unknown",
				error_details: lastAssistant?.errorMessage,
				last_assistant_message: lastText || "",
			});
			for (const group of resolvedConfig()[hookName] ?? []) {
				for (const entry of group.hooks) {
					runHookAsync(entry, failureStdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
				}
			}
		} else {
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
						sendHookMessageToAgent(pi, ctx, result.stderr.trim());
					} else if (result.exitCode !== 0) {
						ctx.ui.notify(`Stop hook error: ${result.stderr}`, "error");
					}
				}
			}
		}

		const notifStdin = JSON.stringify({
			...baseStdin("Notification", ctx),
			title: "Pi",
			message: "Ready for input",
			notification_type: "idle_prompt",
		});
		for (const group of resolvedConfig().Notification ?? []) {
			for (const entry of group.hooks) {
				runHookAsync(entry, notifStdin, (msg, lvl) => ctx.ui.notify(msg, lvl));
			}
		}
	});

	// --- session_before_compact → PreCompact ---
	pi.on("session_before_compact", async (_event: SessionBeforeCompactEvent, ctx: ExtensionContext) => {
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

	// --- input → UserPromptExpansion ---
	pi.on("input", async (event: InputEvent, ctx: ExtensionContext): Promise<InputEventResult | undefined> => {
		const parsed = parseSlashCommand(event.text);
		if (!parsed) return undefined;

		const hookName: HookEventName = "UserPromptExpansion";
		const stdin = JSON.stringify({
			...baseStdin(hookName, ctx),
			expansion_type: "slash_command",
			command_name: parsed.commandName,
			command_args: parsed.commandArgs,
			command_source: event.source,
			prompt: parsed.prompt,
		});

		const groups = matchingGroups(resolvedConfig()[hookName] ?? [], parsed.commandName);
		const result = await runDecisionHooks(hookName, groups, stdin, ctx);
		if (result.additionalContext) {
			pendingPromptExpansionContext = [pendingPromptExpansionContext, result.additionalContext].filter(Boolean).join("\n").trim();
		}
		if (result.blocked) {
			ctx.ui.notify(result.reason ?? "Command expansion blocked by hook", "warning");
			return { action: "handled" };
		}
		return undefined;
	});

	// --- before_agent_start → CwdChanged + UserPromptSubmit ---
	pi.on("before_agent_start", async (event: BeforeAgentStartEvent, ctx: ExtensionContext): Promise<BeforeAgentStartEventResult | undefined> => {
		if (lastHookCwd && lastHookCwd !== ctx.cwd) {
			loadConfig(ctx.cwd);
			const cwdHookName: HookEventName = "CwdChanged";
			const cwdStdin = JSON.stringify({
				...baseStdin(cwdHookName, ctx),
				old_cwd: lastHookCwd,
				new_cwd: ctx.cwd,
			});
			const cwdResult = await runDecisionHooks(cwdHookName, resolvedConfig()[cwdHookName] ?? [], cwdStdin, ctx);
			if (cwdResult.additionalContext) {
				sendHookMessageToAgent(pi, ctx, cwdResult.additionalContext);
			}
		}
		lastHookCwd = ctx.cwd;

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
					// Stdout injected as LLM context
					injected += result.stdout.trim() + "\n";
				} else if (result.exitCode !== 0) {
					ctx.ui.notify(`Prompt hook error: ${result.stderr}`, "error");
				}
			}
		}

		if (pendingPromptExpansionContext.trim()) {
			injected += pendingPromptExpansionContext.trim() + "\n";
			pendingPromptExpansionContext = "";
		}

		if (!injected.trim()) return undefined;
		const text = injected.trim();
		return {
			message: {
				customType: "hook-context",
				content: [{ type: "text", text }],
				display: true,
			},
		};
	});

	// --- tool_call → PreToolUse (blocking + input patching) ---
	pi.on("tool_call", async (event: ToolCallEvent, ctx: ExtensionContext): Promise<ToolCallEventResult | undefined> => {
		const ccName = toCcToolName(event.toolName);
		const stdin = JSON.stringify({
			...baseStdin("PreToolUse", ctx),
			tool_name: ccName,
			tool_input: event.input,
			tool_use_id: event.toolCallId,
		});

		const result = await runPreToolUseGroups(resolvedConfig().PreToolUse ?? [], ccName, stdin, ctx, 10);
		if (result.updatedInput) {
			if (!isRecord(event.input)) {
				return { block: true, reason: "Hook updatedInput rejected: tool input is not a mutable object" };
			}
			replaceInput(event.input, result.updatedInput);
		}
		if (result.blocked) {
			return { block: true, reason: result.reason || "Blocked by hook" };
		}
		if (isRecord(event.input)) {
			toolInputByCallId.set(event.toolCallId, structuredClone(event.input));
		}
		return undefined;
	});

	// --- tool_result → PostToolUse / PostToolUseFailure (LLM feedback loop) ---
	pi.on("tool_result", async (event: ToolResultEvent, ctx: ExtensionContext) => {
		const ccName = toCcToolName(event.toolName);
		const hookName: HookEventName = event.isError ? "PostToolUseFailure" : "PostToolUse";
		// Prefer the pre-hook-patched snapshot from tool_call; only write if absent.
		if (isRecord(event.input) && !toolInputByCallId.has(event.toolCallId)) {
			toolInputByCallId.set(event.toolCallId, structuredClone(event.input));
		}
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
		const extraContexts: string[] = [];

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
					continue;
				}
				if (result.exitCode !== 0) {
					ctx.ui.notify(`Post-tool hook error (${entry.command.split("/").at(-1)}): ${result.stderr}`, "error");
					continue;
				}
				const parsed = parseDecisionOutput(result.stdout, hookName);
				if (parsed.block && parsed.reason) {
					feedbackLines.push(parsed.reason);
				}
				if (parsed.additionalContext) {
					extraContexts.push(parsed.additionalContext);
				}
			}
		}

		if (feedbackLines.length === 0 && extraContexts.length === 0) return undefined;
		const appended: Array<{ type: "text"; text: string }> = [];
		if (feedbackLines.length > 0) {
			appended.push({ type: "text", text: "⚠️ Hook output:\n" + feedbackLines.join("\n---\n") });
		}
		if (extraContexts.length > 0) {
			appended.push({ type: "text", text: extraContexts.join("\n") });
		}
		return {
			content: [...event.content, ...appended],
		};
	});

	// --- turn_end → PostToolBatch ---
	pi.on("turn_end", async (event: TurnEndEvent, ctx: ExtensionContext) => {
		if (!event.toolResults || event.toolResults.length === 0) return;
		const hookName: HookEventName = "PostToolBatch";
		const toolCalls = event.toolResults.map((result) => ({
			tool_name: toCcToolName(result.toolName),
			tool_input: toolInputByCallId.get(result.toolCallId) ?? {},
			tool_use_id: result.toolCallId,
			tool_response: serializeToolContent(result.content as Array<{ type: string; text?: string }>),
			is_error: result.isError,
		}));
		for (const result of event.toolResults) {
			toolInputByCallId.delete(result.toolCallId);
		}
		const stdin = JSON.stringify({
			...baseStdin(hookName, ctx),
			tool_calls: toolCalls,
		});
		const result = await runDecisionHooks(hookName, resolvedConfig()[hookName] ?? [], stdin, ctx);
		if (result.additionalContext) {
			sendHookMessageToAgent(pi, ctx, result.additionalContext);
		}
		if (result.blocked && result.reason) {
			sendHookMessageToAgent(pi, ctx, result.reason);
		}
	});
}
