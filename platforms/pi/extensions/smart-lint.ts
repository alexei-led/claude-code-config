/**
 * Smart Lint Extension
 *
 * Runs smart-lint.sh after every turn that touched a file via write/edit.
 * Mirrors Claude Code's PostToolUse hook for Pi.
 *
 * smart-lint.sh self-filters changed files via git diff and exits 2
 * on blocking errors (Claude Code hook convention).
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { execFileSync } from "node:child_process";
import * as path from "node:path";

export default function (pi: ExtensionAPI) {
	const script = path.resolve(__dirname, "smart-lint.sh");
	let editedThisTurn = false;

	pi.on("tool_call", async (event) => {
		if (event.toolName === "write" || event.toolName === "edit") {
			editedThisTurn = true;
		}
		return undefined;
	});

	pi.on("turn_end", async (_event, ctx) => {
		if (!editedThisTurn) return;
		editedThisTurn = false;

		try {
			execFileSync(script, [], {
				stdio: ["ignore", "pipe", "pipe"],
				cwd: process.cwd(),
				timeout: 60_000,
			});
		} catch (err: any) {
			const stderr = (err?.stderr?.toString?.() ?? "").trim();
			const message = stderr || String(err?.message ?? err);
			if (ctx?.hasUI && ctx.ui?.notify) {
				ctx.ui.notify(`smart-lint: ${message.split("\n")[0]}`, "warning");
			}
			console.error(message);
		}
	});
}
