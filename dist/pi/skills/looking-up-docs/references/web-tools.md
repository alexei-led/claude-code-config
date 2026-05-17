# Per-Platform Web Tool Identifiers

Exact tool names for Tier 2 (Perplexity) and Tier 3 (built-in web) of the
documentation lookup fallback chain. Names differ per agent runtime.

## Claude

- Tier 2 — Perplexity MCP: `mcp__perplexity-ask__perplexity_ask`.
- Tier 3 — built-in: `WebSearch` to find the official docs URL, then
  `WebFetch` to read the page and ground the answer.

## Codex

- Tier 2 — Perplexity MCP, when the Perplexity MCP server is configured for
  Codex.
- Tier 3 — built-in web search (the Codex web search tool, enabled in the
  Codex config). Find the official docs URL and ground the answer in it.

## Gemini

- Tier 2 — Perplexity MCP, when the Perplexity MCP server is configured for
  Gemini.
- Tier 3 — built-in: `google_web_search` to find the official docs URL, then
  `web_fetch` to retrieve and process that page.

## Pi

Pi's web providers are Perplexity-backed, so Tier 2 and Tier 3 share a
provider; escalation is depth, not a different vendor.

- Tier 2 — `web_answer` for a focused factual question; `web_search` for
  source discovery, then read the best official source.
- Tier 3 — `web_research` for a broad or multi-step investigation when the
  focused query was insufficient.

## Notes

- Perplexity availability is not guaranteed on Codex or Gemini; if the MCP
  server is absent, skip Tier 2 and fall to the platform's built-in web tools.
- Always require URL-cited primary sources (official docs, release notes)
  before stating syntax or API behavior.
