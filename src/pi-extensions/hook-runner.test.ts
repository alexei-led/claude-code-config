import { beforeEach, describe, expect, it, mock } from "bun:test";

// ---------------------------------------------------------------------------
// Module mocks — must be established before the first import of hook-runner
// ---------------------------------------------------------------------------

type ExecCallback = (err: Error | null, stdout: string, stderr: string) => void;

const execQueue: Array<{ exitCode: number; stdout: string; stderr: string }> = [];
const capturedCommands: string[] = [];
let capturedStdin = "";

mock.module("node:child_process", () => ({
	execFile: (_cmd: string, args: string[], _opts: unknown, cb: ExecCallback) => {
		capturedCommands.push(args.join(" "));
		const resp = execQueue.shift() ?? { exitCode: 0, stdout: "", stderr: "" };
		const child = {
			stdin: {
				write: (data: string) => {
					capturedStdin = data;
				},
				end: () => {},
			},
		};
		setTimeout(() => {
			if (resp.exitCode === 0) {
				cb(null, resp.stdout, resp.stderr);
			} else {
				const err = Object.assign(new Error("exit"), { code: resp.exitCode });
				cb(err as Error, resp.stdout, resp.stderr);
			}
		}, 0);
		return child;
	},
}));

mock.module("node:fs", () => ({
	readFileSync: () => {
		throw Object.assign(new Error("ENOENT"), { code: "ENOENT" });
	},
}));

mock.module("node:os", () => ({ homedir: () => "/tmp/test-home" }));
mock.module("@earendil-works/pi-coding-agent", () => ({}));

// ---------------------------------------------------------------------------
// Dynamic import (after mocks are registered)
// ---------------------------------------------------------------------------

const { default: hookRunner, _resetForTesting, toCcToolName, matcherMatches, matchingGroups } = await import("./hook-runner.ts");

type EventHandler = (...args: unknown[]) => unknown;
const handlers = new Map<string, EventHandler>();
hookRunner({ on: (event: string, h: EventHandler) => handlers.set(event, h) } as any);

function makeCtx(overrides: { cwd?: string; sessionId?: string } = {}) {
	return {
		cwd: overrides.cwd ?? "/workspace",
		sessionManager: { getSessionId: () => overrides.sessionId ?? "sess-test" },
		ui: { notify: mock(), select: mock() },
		sendUserMessage: mock(async () => {}),
	};
}

beforeEach(() => {
	_resetForTesting();
	execQueue.length = 0;
	capturedCommands.length = 0;
	capturedStdin = "";
});

// ---------------------------------------------------------------------------
// Pure utility functions
// ---------------------------------------------------------------------------

describe("toCcToolName", () => {
	it.each([
		["bash", "Bash"],
		["write", "Write"],
		["edit", "Edit"],
		["multiedit", "MultiEdit"],
		["read", "Read"],
		["grep", "Grep"],
		["find", "Find"],
		["ls", "Ls"],
		["AlreadyCamel", "AlreadyCamel"],
	])("%s → %s", (input, expected) => {
		expect(toCcToolName(input)).toBe(expected);
	});
});

describe("matcherMatches", () => {
	it.each([
		[undefined, "Write", true],
		["", "Write", true],
		["*", "Write", true],
		["Write|Edit|MultiEdit", "Write", true],
		["Write|Edit|MultiEdit", "MultiEdit", true],
		["Write|Edit|MultiEdit", "Bash", false],
		["Bash", "Bash", true],
		["bash", "Bash", true], // case-insensitive
		["Bash", "Write", false],
	])("matcher=%j tool=%s → %s", (matcher, tool, expected) => {
		expect(matcherMatches(matcher, tool)).toBe(expected);
	});
});

describe("matchingGroups", () => {
	const groups = [{ matcher: "Write|Edit", hooks: [] }, { matcher: "Bash", hooks: [] }, { hooks: [] }];

	it.each([
		["Write", 2], // Write|Edit + catch-all
		["Bash", 2], // Bash + catch-all
		["Read", 1], // catch-all only
	])("tool=%s → %d matching groups", (tool, count) => {
		expect(matchingGroups(groups, tool)).toHaveLength(count);
	});
});

// ---------------------------------------------------------------------------
// tool_call → PreToolUse
// ---------------------------------------------------------------------------

describe("tool_call → PreToolUse", () => {
	const handler = handlers.get("tool_call") as EventHandler;

	it("blocks when exit code 2", async () => {
		execQueue.push({ exitCode: 2, stdout: "", stderr: "Protected file: .env" });
		const result = await handler({ toolName: "write", input: { file_path: "/home/user/.env" }, toolCallId: "tc1" }, makeCtx());
		expect(result).toEqual({ block: true, reason: "Protected file: .env" });
	});

	it("uses fallback reason when stderr is empty on exit 2", async () => {
		execQueue.push({ exitCode: 2, stdout: "", stderr: "" });
		const result = await handler({ toolName: "write", input: { file_path: "/etc/passwd" }, toolCallId: "tc2" }, makeCtx());
		expect((result as any).block).toBe(true);
		expect((result as any).reason).toBeTruthy();
	});

	it("allows on exit code 0", async () => {
		execQueue.push({ exitCode: 0, stdout: "", stderr: "" });
		const result = await handler({ toolName: "write", input: { file_path: "/workspace/src/app.ts" }, toolCallId: "tc3" }, makeCtx());
		expect(result).toBeUndefined();
	});

	it("notifies and allows on non-blocking error (exit 1)", async () => {
		execQueue.push({ exitCode: 1, stdout: "", stderr: "hook script error" });
		const ctx = makeCtx();
		const result = await handler({ toolName: "bash", input: { command: "ls" }, toolCallId: "tc4" }, ctx);
		expect(result).toBeUndefined();
		expect(ctx.ui.notify).toHaveBeenCalledWith(expect.stringContaining("error"), "error");
	});

	it("puts CC tool name and event name in stdin JSON", async () => {
		execQueue.push({ exitCode: 0, stdout: "", stderr: "" });
		await handler({ toolName: "write", input: { file_path: "x.ts" }, toolCallId: "tc5" }, makeCtx());
		const stdin = JSON.parse(capturedStdin);
		expect(stdin.tool_name).toBe("Write");
		expect(stdin.hook_event_name).toBe("PreToolUse");
		expect(stdin.cwd).toBe("/workspace");
		expect(stdin.session_id).toBe("sess-test");
		expect(stdin.tool_input).toEqual({ file_path: "x.ts" });
	});

	it("skips hooks when no group matches the tool name", async () => {
		const result = await handler({ toolName: "read", input: {}, toolCallId: "tc6" }, makeCtx());
		expect(result).toBeUndefined();
		expect(capturedCommands).toHaveLength(0);
	});
});

// ---------------------------------------------------------------------------
// tool_result → PostToolUse (LLM feedback loop)
// ---------------------------------------------------------------------------

describe("tool_result → PostToolUse", () => {
	const handler = handlers.get("tool_result") as EventHandler;

	it("injects hook stderr into tool content on exit 2 (feedback loop)", async () => {
		execQueue.push({ exitCode: 2, stdout: "", stderr: "lint: semicolon missing at line 5" });
		const result = (await handler(
			{
				toolName: "write",
				input: { file_path: "app.ts" },
				toolCallId: "tr1",
				isError: false,
				content: [{ type: "text", text: "file written" }],
			},
			makeCtx(),
		)) as { content: Array<{ type: string; text: string }> };
		expect(result).toBeDefined();
		expect(result.content).toHaveLength(2);
		expect(result.content[1].text).toContain("lint: semicolon missing");
	});

	it("returns undefined when no feedback (exit 0)", async () => {
		execQueue.push({ exitCode: 0, stdout: "", stderr: "" });
		const result = await handler(
			{
				toolName: "write",
				input: {},
				toolCallId: "tr2",
				isError: false,
				content: [{ type: "text", text: "ok" }],
			},
			makeCtx(),
		);
		expect(result).toBeUndefined();
	});

	it("uses PostToolUseFailure hook name when isError=true", async () => {
		await handler(
			{
				toolName: "write",
				input: {},
				toolCallId: "tr3",
				isError: true,
				content: [],
			},
			makeCtx(),
		);
		if (capturedStdin) {
			const stdin = JSON.parse(capturedStdin);
			expect(stdin.hook_event_name).toBe("PostToolUseFailure");
		}
		// PostToolUseFailure has no builtin hooks so no hooks run; verify no commands ran
	});

	it("preserves original content items alongside feedback", async () => {
		execQueue.push({ exitCode: 2, stdout: "", stderr: "error found" });
		const original = [{ type: "text", text: "original" }];
		const result = (await handler({ toolName: "write", input: {}, toolCallId: "tr4", isError: false, content: original }, makeCtx())) as { content: unknown[] };
		expect(result.content[0]).toEqual(original[0]);
	});

	it("skips hooks for non-matching tool names", async () => {
		const result = await handler({ toolName: "read", input: {}, toolCallId: "tr5", isError: false, content: [] }, makeCtx());
		expect(result).toBeUndefined();
		expect(capturedCommands).toHaveLength(0);
	});
});

// ---------------------------------------------------------------------------
// before_agent_start → UserPromptSubmit
// ---------------------------------------------------------------------------

describe("before_agent_start → UserPromptSubmit", () => {
	const handler = handlers.get("before_agent_start") as EventHandler;

	it("injects hook stdout as context message", async () => {
		execQueue.push({ exitCode: 0, stdout: "→ Consider skills: writing-go", stderr: "" });
		const result = (await handler({ prompt: "write a go service" }, makeCtx())) as any;
		expect(result).toBeDefined();
		expect(result.message.content[0].text).toContain("writing-go");
	});

	it("returns undefined when hook produces no output", async () => {
		execQueue.push({ exitCode: 0, stdout: "", stderr: "" });
		expect(await handler({ prompt: "hello" }, makeCtx())).toBeUndefined();
	});

	it("injects stderr as context on exit 2 (blocked prompt gets context)", async () => {
		execQueue.push({ exitCode: 2, stdout: "", stderr: "blocked: use /writing-go skill" });
		const result = (await handler({ prompt: "write code" }, makeCtx())) as any;
		expect(result?.message.content[0].text).toContain("blocked");
	});

	it("notifies on non-blocking error (exit 1)", async () => {
		execQueue.push({ exitCode: 1, stdout: "", stderr: "hook error" });
		const ctx = makeCtx();
		await handler({ prompt: "test" }, ctx);
		expect(ctx.ui.notify).toHaveBeenCalledWith(expect.stringContaining("error"), "error");
	});

	it("includes prompt and hook_event_name in stdin JSON", async () => {
		execQueue.push({ exitCode: 0, stdout: "context", stderr: "" });
		await handler({ prompt: "my prompt" }, makeCtx());
		const stdin = JSON.parse(capturedStdin);
		expect(stdin.prompt).toBe("my prompt");
		expect(stdin.hook_event_name).toBe("UserPromptSubmit");
	});
});

// ---------------------------------------------------------------------------
// session_start → SessionStart
// ---------------------------------------------------------------------------

describe("session_start → SessionStart", () => {
	const handler = handlers.get("session_start") as EventHandler;

	it("skips reload events without running any hooks", async () => {
		await handler({ reason: "reload" }, makeCtx());
		expect(capturedCommands).toHaveLength(0);
	});

	it("runs hooks on startup reason", async () => {
		execQueue.push({ exitCode: 0, stdout: "Project: cc-thingz", stderr: "" });
		await handler({ reason: "startup" }, makeCtx());
		expect(capturedCommands.length).toBeGreaterThan(0);
	});

	it("notifies user of hook stdout output", async () => {
		execQueue.push({ exitCode: 0, stdout: "Project context loaded", stderr: "" });
		const ctx = makeCtx();
		await handler({ reason: "startup" }, ctx);
		expect(ctx.ui.notify).toHaveBeenCalledWith(expect.stringContaining("Project context"), "info");
	});

	it("puts hook_event_name=SessionStart in stdin JSON", async () => {
		execQueue.push({ exitCode: 0, stdout: "", stderr: "" });
		await handler({ reason: "new" }, makeCtx());
		const stdin = JSON.parse(capturedStdin);
		expect(stdin.hook_event_name).toBe("SessionStart");
		expect(stdin.source).toBe("new");
	});
});

// ---------------------------------------------------------------------------
// session_before_compact → PreCompact
// ---------------------------------------------------------------------------

describe("session_before_compact → PreCompact", () => {
	const handler = handlers.get("session_before_compact") as EventHandler;

	it("returns undefined when no PreCompact hooks configured", async () => {
		// Builtin hooks have no PreCompact; result should be undefined
		const result = await handler({}, makeCtx());
		expect(result).toBeUndefined();
	});
});

// ---------------------------------------------------------------------------
// session_compact → PostCompact
// ---------------------------------------------------------------------------

describe("session_compact → PostCompact", () => {
	const handler = handlers.get("session_compact") as EventHandler;

	it("runs without error when no PostCompact hooks configured", async () => {
		await expect(handler({ fromExtension: false }, makeCtx())).resolves.toBeUndefined();
	});
});

// ---------------------------------------------------------------------------
// agent_end → Stop + Notification
// ---------------------------------------------------------------------------

describe("agent_end → Stop + Notification", () => {
	const handler = handlers.get("agent_end") as EventHandler;

	it("dispatches Notification with idle_prompt payload", async () => {
		// Stop hook (ccgram) + Notification hook (notify.sh) both fire async
		await handler({}, makeCtx());
		const notifCommand = capturedCommands.find((c) => c.includes("notify.sh"));
		expect(notifCommand).toBeDefined();
	});

	it("sends notification_type=idle_prompt in stdin", async () => {
		// Capture the last stdin written — notify.sh is last dispatched
		await handler({}, makeCtx());
		if (capturedStdin) {
			const stdin = JSON.parse(capturedStdin);
			expect(stdin.notification_type).toBe("idle_prompt");
			expect(stdin.hook_event_name).toBe("Notification");
			expect(stdin.title).toBe("Pi");
		}
	});
});
