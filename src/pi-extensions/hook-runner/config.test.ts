import { describe, expect, it } from "bun:test";

import { parsePackageContribution } from "./config.ts";

describe("parsePackageContribution", () => {
	it("returns undefined for invalid JSON", () => {
		expect(parsePackageContribution("{ not valid")).toBeUndefined();
	});

	it("returns undefined when cc-thingz field absent", () => {
		expect(parsePackageContribution(JSON.stringify({ name: "pkg", version: "1.0.0" }))).toBeUndefined();
	});

	it("returns undefined when cc-thingz.hooks absent", () => {
		expect(parsePackageContribution(JSON.stringify({ "cc-thingz": {} }))).toBeUndefined();
	});

	it("returns undefined when cc-thingz.hooks is not an object", () => {
		expect(parsePackageContribution(JSON.stringify({ "cc-thingz": { hooks: [] } }))).toBeUndefined();
	});

	it("parses a valid contribution", () => {
		const content = JSON.stringify({
			name: "acme",
			"cc-thingz": {
				hooks: {
					PostToolUse: [
						{
							matcher: "Write",
							hooks: [{ type: "command", command: "/usr/local/bin/acme-audit" }],
						},
					],
				},
			},
		});
		const result = parsePackageContribution(content);
		expect(result?.PostToolUse).toBeDefined();
		expect(result?.PostToolUse?.[0].matcher).toBe("Write");
		expect(result?.PostToolUse?.[0].hooks[0].config.command).toBe("/usr/local/bin/acme-audit");
	});

	it("drops malformed entries inside an otherwise-valid contribution", () => {
		const content = JSON.stringify({
			"cc-thingz": {
				hooks: {
					PreToolUse: [
						{ matcher: "Bash", hooks: [{ type: "command" }] }, // missing command
						{ matcher: "Read", hooks: [{ type: "command", command: "/bin/ok" }] },
					],
				},
			},
		});
		const result = parsePackageContribution(content);
		expect(result?.PreToolUse).toBeDefined();
		expect(result?.PreToolUse?.length).toBe(1);
		expect(result?.PreToolUse?.[0].hooks[0].config.command).toBe("/bin/ok");
	});

	it("ignores entries whose hooks list is empty after filtering", () => {
		const content = JSON.stringify({
			"cc-thingz": {
				hooks: {
					PreToolUse: [{ matcher: "Bash", hooks: [{ type: "command" }] }], // command missing → entry dropped
				},
			},
		});
		const result = parsePackageContribution(content);
		// All groups dropped → event entry not present
		expect(result?.PreToolUse).toBeUndefined();
	});
});
