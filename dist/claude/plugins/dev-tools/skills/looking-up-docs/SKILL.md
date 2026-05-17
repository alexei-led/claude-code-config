---
allowed-tools:
- Read
- Grep
- Glob
- Bash(ctx7 *)
- Bash(npx ctx7@latest *)
- Bash(bunx ctx7@latest *)
- mcp__perplexity-ask__perplexity_ask
- WebSearch
- WebFetch
description: Find current, factual library/API/framework documentation through a tool-fallback
  chain. Use when the user says "look up docs", "how to use", "API for", "syntax for",
  "examples of", "show me the docs", or wants the latest/current/actual behavior of
  a library, framework, CLI, or API. NOT for comparisons, best-practice surveys, or
  recent ecosystem news — use researching-web. NOT for raw ctx7 CLI mechanics — that
  is context7-cli.
name: looking-up-docs
---

# Documentation Lookup

Get grounded, version-correct documentation for a library, framework, CLI, or
API. Training data goes stale; never answer syntax or API questions from memory
when a lookup tool is available.

This skill owns the lookup flow. Tool mechanics live elsewhere: `ctx7` command
detail is in the `context7-cli` skill; exact per-platform web tool names are in
`references/web-tools.md`.

## Scope

Use this skill for:

- API signatures, options, config keys, syntax, and examples.
- Version-specific behavior of a known library or framework.
- Confirming current behavior before writing code against an external API.

Do not use this skill as the primary workflow for:

- Comparisons, recommendations, market research, or best-practice surveys —
  route to `researching-web`.
- Repo-specific questions — search local files first.
- Anything that would require sending secrets, credentials, personal data, or
  proprietary code to an external service.

## Fallback Chain

Run the tiers in order. Stop at the first tier that yields a grounded answer.
State which tier produced the answer and whether any fallback was used.

### Tier 1 — Context7 (`ctx7`)

Best for versioned library and framework docs. Follow the `context7-cli`
workflow: identify the library and version from project files, resolve a
library ID with `ctx7 library`, then fetch docs with `ctx7 docs`. Show the
exact commands. See the `context7-cli` skill for command detail and limits.

Escalate to Tier 2 when: `ctx7` is unavailable or not on `PATH` and the
package-runner fallback also fails; the CLI hits a rate or auth limit; or it
returns no useful match after one rephrase and one alternate library name.

### Tier 2 — Perplexity

Best for official docs, release notes, and current behavior not covered by
Context7. Query Perplexity with a focused, version-qualified question and
require URL-cited sources. The exact tool differs per platform — Perplexity MCP
on Claude, Codex, and Gemini; the Perplexity-backed web provider on Pi. See
`references/web-tools.md`.

Escalate to Tier 3 when: Perplexity is unavailable or unconfigured; it returns
no usable citation; or the answer needs a specific page fetched verbatim.

### Tier 3 — Platform built-in web tools

Last resort. Every supported agent ships native web search and fetch: Claude
`WebSearch` + `WebFetch`; Codex built-in web search; Gemini `google_web_search`
+ `web_fetch`; Pi `web_search` / `web_research`. See `references/web-tools.md`
for exact identifiers. Find the official documentation URL, fetch it, and
ground the answer in the fetched page. Quote only the relevant part and cite
the URL.

## Hard Limits

- Never send secrets, credentials, private payloads, personal data, or
  proprietary code to any tier.
- Always pass a real, specific query — never a one-word placeholder.
- Do not loop a tier indefinitely: one rephrase and one alternate name per
  tier, then escalate.
- Prefer primary sources (official docs, release notes) over blogs.
- If all tiers fail, report the gap and the exact version mismatch — do not
  fabricate syntax.

## Response Contract

For a docs lookup, return:

1. Library / framework / API and version identified, or state version unknown.
2. Tier that produced the answer, and any fallback used.
3. Concise syntax or example guidance grounded in the source.
4. Source URL or library ID for the grounded claim.
5. Boundary note when the request is actually comparison or broad research.

If the user asks to describe the workflow, describe these tiers and the
escalation rules instead of answering from memory.

## Failure Cases

- All tiers exhausted with no grounded answer: report the gap, state the
  version needed vs found, and do not invent syntax.
- Returned docs are version-mismatched: note the discrepancy explicitly and
  escalate to the next tier for the specific version's release notes.
- Request requires private code or credentials: refuse the external query and
  answer from local context only, noting the limitation.
