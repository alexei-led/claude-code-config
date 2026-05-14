import { describe, expect, it } from "bun:test";

import { buildTelemetryLine, extractProgress } from "./dispatch.ts";
import type { HookEntryRuntime, HookRunResult } from "./types.ts";

describe("extractProgress", () => {
	it("returns stderr unchanged when no progress markers present", () => {
		const result = extractProgress("normal stderr output");
		expect(result.stderr).toBe("normal stderr output");
		expect(result.last).toBeUndefined();
	});

	it("strips progress lines and returns the last update", () => {
		const stderr = ["starting", "^^PROGRESS 10 reading input", "more noise", "^^PROGRESS 50 halfway", "^^PROGRESS 100 done", "trailer"].join("\n");
		const result = extractProgress(stderr);
		expect(result.stderr).toBe(["starting", "more noise", "trailer"].join("\n"));
		expect(result.last).toEqual({ percent: 100, message: "done" });
	});

	it("clamps percent to 0-100 range", () => {
		const result = extractProgress("^^PROGRESS 999 boom");
		expect(result.last?.percent).toBe(100);
	});

	it("ignores malformed progress markers", () => {
		const result = extractProgress("^^PROGRESS notanumber message");
		expect(result.last).toBeUndefined();
		expect(result.stderr).toContain("^^PROGRESS notanumber");
	});

	it("handles CRLF line endings", () => {
		const stderr = "step1\r\n^^PROGRESS 25 quarter\r\nstep2";
		const result = extractProgress(stderr);
		expect(result.last).toEqual({ percent: 25, message: "quarter" });
		expect(result.stderr).toBe("step1\nstep2");
	});

	it("trims trailing whitespace in the message", () => {
		const result = extractProgress("^^PROGRESS 30 trimmed   ");
		expect(result.last?.message).toBe("trimmed");
	});
});

describe("buildTelemetryLine", () => {
	const fixedNow = () => new Date("2026-05-14T20:00:00.000Z");

	it("uses the entry's event name, not the command path", () => {
		// Regression: telemetry once wrote `entry.config.command` as the event,
		// burying every hook run under its script path instead of `PreToolUse`.
		const entry: HookEntryRuntime = {
			config: { type: "command", command: "/abs/path/to/script.py", timeout: 30 },
			source: "bundled",
			disabled: false,
			eventName: "PreToolUse",
		};
		const result: HookRunResult = { exitCode: 0, stdout: "", stderr: "", timedOut: false };

		const line = buildTelemetryLine(entry, result, 42, fixedNow);
		const parsed = JSON.parse(line) as Record<string, unknown>;
		expect(parsed.event).toBe("PreToolUse");
		expect(parsed.hook).toBe("script.py");
		expect(parsed.source).toBe("bundled");
		expect(parsed.exit_code).toBe(0);
		expect(parsed.duration_ms).toBe(42);
		expect(parsed.timed_out).toBe(false);
		expect(parsed.ts).toBe("2026-05-14T20:00:00.000Z");
	});

	it("preserves the timed_out and exit_code signals", () => {
		const entry: HookEntryRuntime = {
			config: { type: "command", command: "/x/y" },
			source: "global",
			disabled: false,
			eventName: "Stop",
		};
		const line = buildTelemetryLine(entry, { exitCode: 124, stdout: "", stderr: "kill", timedOut: true }, 1, fixedNow);
		const parsed = JSON.parse(line) as { event: string; timed_out: boolean; exit_code: number };
		expect(parsed.event).toBe("Stop");
		expect(parsed.timed_out).toBe(true);
		expect(parsed.exit_code).toBe(124);
	});

	it("truncates stderr to STDERR_HEAD_LIMIT", () => {
		const entry: HookEntryRuntime = {
			config: { type: "command", command: "/x/loud.py" },
			source: "project",
			disabled: false,
			eventName: "PostToolUse",
		};
		const noisy = "x".repeat(2000);
		const line = buildTelemetryLine(entry, { exitCode: 1, stdout: "", stderr: noisy, timedOut: false }, 5, fixedNow);
		const parsed = JSON.parse(line) as { stderr_head: string };
		expect(parsed.stderr_head.length).toBeLessThanOrEqual(500);
	});
});
