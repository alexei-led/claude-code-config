# MCP → CLI/Skill Migration Backlog

`cc-thingz` is moving toward CLI- and skill-based wrappers over MCP servers
for portability across Claude Code, Codex, Gemini, and Pi. The Pi overlay
generator already strips MCP references from Pi exports, so Pi is unaffected
by the items below — these are about reducing MCP surface area in the
**Claude Code** source.

## Status snapshot (2026-05-09)

| MCP namespace                                                                                           | CLI alternative                                              | Migration status                                                                                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mcp__context7__*`                                                                                      | `ctx7` (and `npx ctx7@latest`)                               | **Done** — skills and 13 source agents now use the CLI; locked by `tests/test_no_mcp_context7_in_plugins.py`.                                                                                                                                                                                           |
| `mcp__playwright__*`                                                                                    | `npx playwright` via `playwright-skill` / `testing-e2e`      | **Done** — never used MCP in this repo; CLI-only since inception.                                                                                                                                                                                                                                       |
| `mcp__perplexity-ask__perplexity_ask`                                                                   | None official                                                | **Open** — no Anthropic-supported CLI. For Pi, the overlay can rewrite to `web_research`/`web_search`. For Claude Code, keep MCP until a CLI lands or wrap a third-party `pplx`-style binary in a skill.                                                                                                |
| `mcp__morphllm__codebase_search`, `mcp__morphllm__warpgrep_codebase_search`, `mcp__morphllm__edit_file` | [`morph` CLI](https://docs.morphllm.com/)                    | **Open** — Morph publishes a CLI; needs a `morph-cli` skill that wraps `morph search` / `morph edit`. Unblock by adding the skill, then drop MCP from `searching-code` and `refactoring-code`.                                                                                                          |
| `mcp__plugin_claude-mem_mcp-search__*`                                                                  | [`claude-mem`](https://github.com/thedotmack/claude-mem) CLI | **Open** — claude-mem ships a CLI; wrap it in a skill (or extend `mem-history`) that calls `claude-mem search` / `claude-mem outline` / `claude-mem unfold`. Drop MCP from agents using these tools after the skill lands.                                                                              |
| `mcp__deepwiki__*`                                                                                      | None                                                         | **Deferred** — DeepWiki is HTTP-only via Devin. Keep MCP for `exploring-repos` and `gh` CLI fallback. Revisit if a CLI ships.                                                                                                                                                                           |
| `mcp__sequential-thinking__sequentialthinking`                                                          | None — pure prompting                                        | **Done** — replaced by the [`sequential-thinking` skill](../plugins/dev-tools/skills/sequential-thinking/SKILL.md). Numbered Thought blocks with revisions/branches via prompting; portable across Claude Code, Codex, Gemini, and Pi. Locked by `tests/test_no_mcp_sequential_thinking_in_plugins.py`. |

## Notes

- MCP servers are still useful for Claude Code where they're already installed,
  but they're an obstacle for Codex/Gemini/Pi portability. Wrapping each MCP
  capability in a skill that drives a CLI keeps source skills usable everywhere
  without per-platform overlays.
- The Pi overlay (`scripts/generate-overlays.py --platform pi`) strips MCP tool
  names from `allowed-tools` and Pi-only banners. Pi agents (`scripts/generate-pi-agents.py`)
  refuse to export agents that name unsupported tools without a `<agent>.pi.md`
  override.
- When introducing a new CLI-backed skill, mirror the `context7-cli`/`looking-up-docs`
  pair: a primary skill that wraps the CLI directly, and a router skill that
  preserves a friendlier trigger name and routes to the primary.
