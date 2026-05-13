import { beforeEach, describe, expect, it, mock } from "bun:test";

// Must precede import of the module under test
mock.module("@earendil-works/pi-coding-agent", () => ({}));

const { default: permissionGate } = await import("./permission-gate.ts");

type Handler = (event: { toolName: string; input: Record<string, unknown> }, ctx: unknown) => Promise<unknown>;
const handlers = new Map<string, Handler>();

permissionGate({ on: (event: string, handler: Handler) => handlers.set(event, handler) } as any);

function makeCtx(hasUI: boolean, selectResult?: string) {
	return {
		hasUI,
		ui: {
			select: mock(async () => selectResult),
			notify: mock(),
		},
	};
}

describe("permission-gate / tool_call", () => {
	const handler = handlers.get("tool_call")!;

	it("allows non-bash tools unconditionally", async () => {
		expect(await handler({ toolName: "write", input: {} }, makeCtx(false))).toBeUndefined();
		expect(await handler({ toolName: "read", input: {} }, makeCtx(false))).toBeUndefined();
	});

	it("allows safe bash commands without prompting", async () => {
		const ctx = makeCtx(true);
		const result = await handler({ toolName: "bash", input: { command: "ls -la" } }, ctx);
		expect(result).toBeUndefined();
		expect(ctx.ui.select).not.toHaveBeenCalled();
	});

	it.each([
		["rm -rf /tmp/build", "rm -rf"],
		["rm -r node_modules", "rm -r"],
		["sudo apt install curl", "sudo"],
		["chmod 777 /etc/passwd", "chmod 777"],
		["chown 777 /etc/hosts", "chown 777"],
	])("blocks dangerous command in no-UI mode: %s (%s)", async (command) => {
		const result = await handler({ toolName: "bash", input: { command } }, makeCtx(false));
		expect(result).toMatchObject({ block: true });
	});

	it("prompts user in UI mode and allows when user confirms", async () => {
		const ctx = makeCtx(true, "Yes");
		const result = await handler({ toolName: "bash", input: { command: "sudo whoami" } }, ctx);
		expect(ctx.ui.select).toHaveBeenCalledTimes(1);
		expect(result).toBeUndefined();
	});

	it("prompts user in UI mode and blocks when user declines", async () => {
		const ctx = makeCtx(true, "No");
		const result = await handler({ toolName: "bash", input: { command: "sudo rm -rf /" } }, ctx);
		expect(result).toMatchObject({ block: true, reason: "Blocked by user" });
	});

	it("blocks when UI select returns undefined (dismissed)", async () => {
		const ctx = makeCtx(true, undefined);
		const result = await handler({ toolName: "bash", input: { command: "sudo echo hi" } }, ctx);
		expect(result).toMatchObject({ block: true });
	});

	beforeEach(() => {
		// Clear handler state between tests
		handlers.clear();
		permissionGate({ on: (event: string, handler: Handler) => handlers.set(event, handler) } as any);
	});
});
