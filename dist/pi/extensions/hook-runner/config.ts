/**
 * Hook-runner configuration: discovery, merge, persistence, summary.
 *
 * Module-level cache. Loaded lazily on first session_start (or forced reload
 * on ConfigChange), keyed by cwd. The cache is process-local — Pi reuses
 * the same Node runtime across sessions.
 */

import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve as resolvePath } from "node:path";
import { fileURLToPath } from "node:url";

import type { HookEntryConfig, HookEntryRuntime, HookGroup, HooksConfig, HookRunnerOptions, HookSource } from "./types.js";
import { isRecord } from "./types.js";

// ---------------------------------------------------------------------------
// Path resolution — works regardless of where Pi cloned the package
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// dist/pi/extensions/hook-runner/config.ts → ../../hooks → dist/pi/hooks
export const HOOKS_DIR = join(__dirname, "..", "..", "hooks");
export const BUNDLED_HOOKS_CONFIG_PATH = join(__dirname, "..", "hooks.json");
export const PI_HOOKS_DIR_PLACEHOLDER = "${PI_HOOKS_DIR}";
export const FORCED_RELOAD_DEBOUNCE_MS = 500;

export function agentDir(): string {
	return process.env.PI_CODING_AGENT_DIR || join(homedir(), ".pi", "agent");
}

export function projectHooksConfigPath(cwd: string): string {
	return join(cwd, ".pi", "hooks.json");
}

export function globalHooksConfigPath(): string {
	return join(agentDir(), "hooks.json");
}

// ---------------------------------------------------------------------------
// Module state
// ---------------------------------------------------------------------------

let _config: HooksConfig | null = null;
/** Pre-filter view (disabled entries still present) — used for /hooks summary. */
let _configRaw: HooksConfig | null = null;
let _configLoadedForCwd = "";
let _ifWarningShown = false;
let _lastForcedReloadMs = 0;
let _bundledCache: HooksConfig | null = null;

export function _resetForTesting(): void {
	_config = null;
	_configRaw = null;
	_configLoadedForCwd = "";
	_ifWarningShown = false;
	_lastForcedReloadMs = 0;
	_bundledCache = null;
}

// ---------------------------------------------------------------------------
// Parsing & normalisation
// ---------------------------------------------------------------------------

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
			const validEntries: HookEntryRuntime[] = [];
			for (const entry of group.hooks) {
				if (!isRecord(entry) || typeof entry.command !== "string") continue;
				const config: HookEntryConfig = {
					type: "command",
					command: entry.command,
				};
				if (typeof entry.timeout === "number") config.timeout = entry.timeout;
				if (typeof entry.async === "boolean") config.async = entry.async;
				// Source/disabled are filled in later by tagEntries / applyDisabled.
				validEntries.push({ config, source: "bundled", disabled: false });
			}
			if (validEntries.length === 0) continue;
			validGroups.push({
				matcher: typeof group.matcher === "string" ? group.matcher : undefined,
				hooks: validEntries,
			});
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
				config: {
					...entry.config,
					command: entry.config.command.replaceAll(PI_HOOKS_DIR_PLACEHOLDER, HOOKS_DIR),
				},
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

export function readHookRunnerOptions(path: string): HookRunnerOptions {
	try {
		const raw = readFileSync(path, "utf-8");
		const parsed = JSON.parse(raw) as unknown;
		return extractHookRunnerOptions(parsed);
	} catch {
		return {};
	}
}

export function readProjectHookRunnerOptions(cwd: string): HookRunnerOptions {
	return readHookRunnerOptions(projectHooksConfigPath(cwd));
}

function tagEntries(config: HooksConfig, source: HookSource): HooksConfig {
	const out: HooksConfig = {};
	for (const [eventName, groups] of Object.entries(config)) {
		if (!groups) continue;
		out[eventName] = groups.map((group) => ({
			matcher: group.matcher,
			hooks: group.hooks.map((entry) => ({ ...entry, source })),
		}));
	}
	return out;
}

export function basename(commandPath: string): string {
	const trimmed = commandPath.trim().split(/\s+/)[0] ?? "";
	return trimmed.split("/").pop() ?? trimmed;
}

function applyDisabled(config: HooksConfig, disabled: Set<string>): void {
	if (disabled.size === 0) return;
	for (const groups of Object.values(config)) {
		if (!groups) continue;
		for (const group of groups) {
			for (const entry of group.hooks) {
				if (disabled.has(basename(entry.config.command))) {
					entry.disabled = true;
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
				hooks: group.hooks.filter((entry) => !entry.disabled),
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
	if (_bundledCache) return _bundledCache;
	try {
		const raw = readFileSync(BUNDLED_HOOKS_CONFIG_PATH, "utf-8");
		const parsed = JSON.parse(raw) as unknown;
		const bundled = extractHooksConfig(parsed, BUNDLED_HOOKS_CONFIG_PATH);
		_bundledCache = resolveBundledHookPaths(bundled);
	} catch {
		_bundledCache = {};
	}
	return _bundledCache;
}

function hasUnsupportedIfPredicate(config: HooksConfig): boolean {
	return Object.values(config)
		.flat()
		.flatMap((g) => g?.hooks ?? [])
		.some((h) => "if" in h.config);
}

function mergeHooks(base: HooksConfig, user: HooksConfig): void {
	for (const [key, groups] of Object.entries(user)) {
		if (!groups) continue;
		const existing = base[key];
		base[key] = existing ? [...existing, ...groups] : [...groups];
	}
}

/**
 * Scan installed Pi packages for hook contributions.
 *
 * A Pi package may declare `cc-thingz.hooks: { <eventName>: HookGroup[] }`
 * inside its `package.json`; cc-thingz merges those entries with `source:
 * "package"` so a plugin can register hooks without editing cc-thingz.
 *
 * Layout: Pi installs each git package under `~/.pi/agent/git/<host>/<org>/<repo>/`,
 * so we look three levels deep from `agentDir()/git/`. Errors during scan
 * are silently swallowed — a misshapen package.json must never break
 * session_start.
 */
export function discoverPackageHookContributions(): HooksConfig {
	const base = join(agentDir(), "git");
	if (!existsSync(base)) return {};
	const merged: HooksConfig = {};
	try {
		for (const host of readdirSync(base)) {
			const hostDir = join(base, host);
			if (!safeIsDirectory(hostDir)) continue;
			for (const org of readdirSync(hostDir)) {
				const orgDir = join(hostDir, org);
				if (!safeIsDirectory(orgDir)) continue;
				for (const repo of readdirSync(orgDir)) {
					const repoDir = join(orgDir, repo);
					if (!safeIsDirectory(repoDir)) continue;
					const contributed = readPackageContribution(repoDir);
					if (contributed) {
						mergeHooks(merged, contributed);
					}
				}
			}
		}
	} catch {
		// Best-effort scan.
	}
	return merged;
}

function safeIsDirectory(path: string): boolean {
	try {
		return statSync(path).isDirectory();
	} catch {
		return false;
	}
}

function readPackageContribution(repoDir: string): HooksConfig | undefined {
	const manifest = join(repoDir, "package.json");
	if (!existsSync(manifest)) return undefined;
	try {
		const raw = readFileSync(manifest, "utf-8");
		return parsePackageContribution(raw, repoDir);
	} catch {
		return undefined;
	}
}

export const PKG_DIR_PLACEHOLDER = "${PKG_DIR}";
// Shell metacharacters that change interpretation when passed to `bash -c`.
// Plugin-contributed commands run inside the user's shell so any of these is
// a potential injection vector from a malicious package.
const PACKAGE_CMD_FORBIDDEN_RE = /[;&|<>`$()\\{}]/;

/**
 * Validate a package-contributed hook command.
 *
 * Returns the resolved command string when safe, or `undefined` when the
 * command would escape the package's directory or contain shell metachars.
 * Plugin authors can use `${PKG_DIR}` as a stand-in for the package root;
 * everything else must be an absolute path that resolves inside `repoDir`.
 */
export function validatePackageCommand(command: string, repoDir: string): string | undefined {
	if (typeof command !== "string") return undefined;
	const substituted = command.replaceAll(PKG_DIR_PLACEHOLDER, repoDir);
	const trimmed = substituted.trim();
	if (!trimmed) return undefined;
	if (PACKAGE_CMD_FORBIDDEN_RE.test(substituted)) return undefined;
	const firstToken = trimmed.split(/\s+/)[0] ?? "";
	if (!firstToken.startsWith("/")) return undefined;
	const repoAbs = resolvePath(repoDir);
	const cmdAbs = resolvePath(firstToken);
	if (cmdAbs !== repoAbs && !cmdAbs.startsWith(repoAbs + "/")) return undefined;
	return substituted;
}

function sanitisePackageContribution(config: HooksConfig, repoDir: string): HooksConfig {
	const out: HooksConfig = {};
	for (const [eventName, groups] of Object.entries(config)) {
		if (!groups) continue;
		const cleanGroups: HookGroup[] = [];
		for (const group of groups) {
			const cleanHooks: HookEntryRuntime[] = [];
			for (const entry of group.hooks) {
				const safe = validatePackageCommand(entry.config.command, repoDir);
				if (!safe) continue;
				cleanHooks.push({
					...entry,
					config: { ...entry.config, command: safe },
				});
			}
			if (cleanHooks.length === 0) continue;
			cleanGroups.push({ matcher: group.matcher, hooks: cleanHooks });
		}
		if (cleanGroups.length > 0) out[eventName] = cleanGroups;
	}
	return out;
}

/**
 * Parse a `package.json` body looking for `cc-thingz.hooks` contributions.
 *
 * When `repoDir` is provided, every contributed command must either be an
 * absolute path inside `repoDir` or use the `${PKG_DIR}` placeholder; commands
 * with shell metacharacters are rejected. When `repoDir` is omitted the parser
 * skips path validation — useful for round-trip parsing in tooling tests but
 * never the path taken at runtime.
 */
export function parsePackageContribution(packageJsonContent: string, repoDir?: string): HooksConfig | undefined {
	try {
		const parsed = JSON.parse(packageJsonContent) as unknown;
		if (!isRecord(parsed)) return undefined;
		const ccThingz = parsed["cc-thingz"];
		if (!isRecord(ccThingz)) return undefined;
		const hooks = ccThingz.hooks;
		if (!isRecord(hooks)) return undefined;
		const normalized = normalizeHookConfig(hooks);
		if (repoDir === undefined) return normalized;
		const cleaned = sanitisePackageContribution(normalized, repoDir);
		return Object.keys(cleaned).length > 0 ? cleaned : undefined;
	} catch {
		return undefined;
	}
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function loadConfig(cwd: string, force = false): void {
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

	// Plugin-contributed hooks land between bundled and user configs: user
	// configs still win on conflict, but plugins can extend the default set
	// without cc-thingz edits.
	const packageContributions = discoverPackageHookContributions();
	if (Object.keys(packageContributions).length > 0) {
		mergeHooks(base, tagEntries(packageContributions, "package"));
	}

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

/**
 * Debounced force-reload trigger — used by the ConfigChange synthetic-hook
 * path so repeated config writes don't thrash the disk.
 */
export function shouldForceReloadForConfigChange(): boolean {
	const now = Date.now();
	if (now - _lastForcedReloadMs >= FORCED_RELOAD_DEBOUNCE_MS) {
		_lastForcedReloadMs = now;
		return true;
	}
	return false;
}

export function resolvedConfig(): HooksConfig {
	return _config ?? loadBundledHooksConfig();
}

export function rawConfig(): HooksConfig {
	return _configRaw ?? loadBundledHooksConfig();
}

// ---------------------------------------------------------------------------
// Persistence + summary
// ---------------------------------------------------------------------------

export function writeHooksConfig(path: string, parsed: Record<string, unknown>): void {
	mkdirSync(dirname(path), { recursive: true });
	writeFileSync(path, JSON.stringify(parsed, null, 2) + "\n", "utf-8");
}

export function hooksSummary(config: HooksConfig): string {
	const lines: string[] = [];
	const events = Object.keys(config).sort();
	for (const eventName of events) {
		const groups = config[eventName];
		if (!groups || groups.length === 0) continue;
		lines.push(`${eventName}:`);
		for (const group of groups) {
			const matcher = group.matcher ? `[${group.matcher}]` : "[*]";
			for (const entry of group.hooks) {
				const status = entry.disabled ? " (disabled)" : "";
				const flags = entry.config.async ? " async" : "";
				lines.push(`  ${matcher} ${basename(entry.config.command)} (${entry.source})${flags}${status}`);
			}
		}
	}
	if (lines.length === 0) return "No hooks configured.";
	return lines.join("\n");
}

export interface HookNameEntry {
	name: string;
	disabled: boolean;
	source: HookSource;
}

export function listAllHookNames(config: HooksConfig): HookNameEntry[] {
	const seen = new Map<string, HookNameEntry>();
	for (const groups of Object.values(config)) {
		if (!groups) continue;
		for (const group of groups) {
			for (const entry of group.hooks) {
				const name = basename(entry.config.command);
				if (!name) continue;
				const existing = seen.get(name);
				if (!existing) {
					seen.set(name, { name, disabled: entry.disabled, source: entry.source });
				} else if (entry.disabled) {
					existing.disabled = true;
				}
			}
		}
	}
	return [...seen.values()].sort((a, b) => a.name.localeCompare(b.name));
}

/** existsSync wrapper for callers that want to check before reading. */
export function pathExists(path: string): boolean {
	return existsSync(path);
}
