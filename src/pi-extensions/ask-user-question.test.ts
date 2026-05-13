import { describe, expect, it, mock } from "bun:test";

// typebox is a Pi peer dep, not installed in the project — mock before importing
mock.module("typebox", () => ({
	Type: {
		Object: (s: unknown) => s,
		String: () => ({}),
		Optional: (s: unknown) => s,
		Array: (s: unknown) => ({ items: s }),
		Boolean: () => ({}),
	},
}));
mock.module("@earendil-works/pi-coding-agent", () => ({}));

const { parseMultiSelect } = await import("./ask-user-question.ts");

const OPTIONS = [
	{ label: "Alpha", value: "alpha" },
	{ label: "Beta", value: "beta" },
	{ label: "Gamma" }, // value defaults to label
];

describe("parseMultiSelect", () => {
	it("parses single numeric index", () => {
		expect(parseMultiSelect("1", OPTIONS)).toEqual([{ label: "Alpha", value: "alpha", source: "option" }]);
	});

	it("parses multiple numeric indices", () => {
		const result = parseMultiSelect("1,3", OPTIONS);
		expect(result).toEqual([
			{ label: "Alpha", value: "alpha", source: "option" },
			{ label: "Gamma", value: "Gamma", source: "option" },
		]);
	});

	it("parses option labels case-insensitively", () => {
		const result = parseMultiSelect("BETA,alpha", OPTIONS);
		expect(result).toHaveLength(2);
		expect(result[0]).toMatchObject({ label: "Beta", source: "option" });
		expect(result[1]).toMatchObject({ label: "Alpha", source: "option" });
	});

	it("treats unrecognized input as custom value", () => {
		expect(parseMultiSelect("something custom", OPTIONS)).toEqual([{ label: "something custom", value: "something custom", source: "custom" }]);
	});

	it("mixes numeric index, label, and custom", () => {
		const result = parseMultiSelect("1, beta, custom thing", OPTIONS);
		expect(result).toHaveLength(3);
		expect(result[0]).toMatchObject({ source: "option", label: "Alpha" });
		expect(result[1]).toMatchObject({ source: "option", label: "Beta" });
		expect(result[2]).toMatchObject({ source: "custom", label: "custom thing" });
	});

	it("deduplicates repeated selections (numeric)", () => {
		expect(parseMultiSelect("1,1", OPTIONS)).toHaveLength(1);
	});

	it("deduplicates repeated selections (label after index)", () => {
		expect(parseMultiSelect("1,alpha", OPTIONS)).toHaveLength(1);
	});

	it("defaults value to label when option has no value field", () => {
		const [item] = parseMultiSelect("3", OPTIONS);
		expect(item.value).toBe("Gamma");
		expect(item.label).toBe("Gamma");
	});

	it("returns empty array for empty input", () => {
		expect(parseMultiSelect("", OPTIONS)).toEqual([]);
	});

	it("returns empty array for whitespace-only input", () => {
		expect(parseMultiSelect("   ", OPTIONS)).toEqual([]);
	});

	it("ignores out-of-range numeric index — treats as custom", () => {
		const result = parseMultiSelect("99", OPTIONS);
		expect(result[0]).toMatchObject({ source: "custom", label: "99" });
	});

	it("handles options array with single entry", () => {
		const result = parseMultiSelect("1", [{ label: "Only" }]);
		expect(result[0]).toMatchObject({ label: "Only", value: "Only", source: "option" });
	});
});
