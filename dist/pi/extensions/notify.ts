/**
 * Notification extension for Pi — fires terminal-notifier on agent_end.
 * Mirrors notify.sh: project name in title, Kitty + tmux click-to-navigate.
 */

import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { execFile, execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { basename } from "node:path";

function hasTerminalNotifier(): boolean {
	try {
		execFileSync("which", ["terminal-notifier"], { stdio: "ignore" });
		return true;
	} catch {
		return false;
	}
}

function buildExecuteCmd(): string {
	const kittySocket =
		process.env.KITTY_LISTEN_ON ??
		(process.env.KITTY_PID ? `unix:/tmp/kitty-${process.env.KITTY_PID}` : "");
	const kittySocketPath = kittySocket.replace(/^unix:/, "");

	if (!kittySocket || !existsSync(kittySocketPath)) return "";

	const kittyBin = process.env.KITTY_BIN ?? "/opt/homebrew/bin/kitty";
	const tmuxBin = "/opt/homebrew/bin/tmux";

	const parts = ["/usr/bin/open -b net.kovidgoyal.kitty"];
	if (process.env.KITTY_WINDOW_ID) {
		parts.push(
			`${kittyBin} @ --to ${kittySocket} focus-tab -m window_id:${process.env.KITTY_WINDOW_ID} 2>/dev/null`,
		);
	}
	if (process.env.TMUX_PANE) {
		parts.push(`${tmuxBin} select-pane -t ${process.env.TMUX_PANE} 2>/dev/null`);
	}
	return parts.join("; ");
}

function notify(cwd: string): void {
	if (!hasTerminalNotifier()) return;

	const project = basename(cwd);
	const title = `[${project}] Pi`;
	const message = "Ready for input";

	const args = [
		"-title",
		title,
		"-message",
		message,
		"-sound",
		"default",
		"-group",
		"pi-agent",
		"-activate",
		"net.kovidgoyal.kitty",
	];

	const executeCmd = buildExecuteCmd();
	if (executeCmd) args.push("-execute", executeCmd);

	execFile("terminal-notifier", args, { env: process.env }, () => {});
}

export default function (pi: ExtensionAPI) {
	pi.on("agent_end", async () => {
		notify(process.cwd());
	});
}
