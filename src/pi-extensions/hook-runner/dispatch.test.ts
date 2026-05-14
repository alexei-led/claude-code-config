import { describe, expect, it } from "bun:test";

import { extractProgress } from "./dispatch.ts";

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
