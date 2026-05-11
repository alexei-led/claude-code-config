# Code Review

## Workflow (\_+)

Track progress through the workflow phases using `TaskCreate` / `TaskUpdate`.

If `$ARGUMENTS` is passed, the keywords below tune the workflow:

- `deep` — use the thorough-review agent set (full dimension coverage per language).
- `team` — run the reviewers as an agent team that challenges each other's findings and converges on consensus.
- `external` — additionally spawn external AI reviewers. Only when explicitly requested; never run by default.
- `architecture` — pass the Architecture vocabulary into every reviewer's prompt.

Without `external`, run only the language reviewers from this skill. Never spawn external reviewers implicitly.

## Determine scope (\_+)

Use `AskUserQuestion` with header "Review scope" and the three options spelled out above.

## Delegate to reviewer agents (\_+)

Spawn each agent via `Task(subagent_type="<name>", prompt=...)`. Each agent's model is set in its own metadata; do not pin a model from the skill.

When `team` is set, spawn the reviewers as an agent team so they challenge each other's findings; report format prefixes findings with `[Flagged by: agent1, agent2]`.

When `external` is set, additionally spawn in parallel:

- `Task(subagent_type="codex-assistant", prompt="review: code from <git_command>")` — security, quality, architecture from a second model.
- `Task(subagent_type="gemini-consultant", prompt="review: architecture of <git_command>")` — architecture alternatives and trade-offs.

## Historical context (optional) (\_+)

If `mcp__plugin_claude-mem_mcp-search__search` is available, query for past findings on the files being reviewed:

```text
search({ query: "<file paths from git diff --name-only HEAD>", limit: 10 })
```

Fetch full observations via `get_observations` for relevant hits. Forward key findings into reviewer prompts. Skip silently if the MCP is not installed.
