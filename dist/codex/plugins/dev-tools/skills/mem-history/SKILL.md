---
description: Query project history, past decisions, and known gotchas from claude-mem
  observations. Use when user asks "last session", "did we already", "what did we
  decide", "project history", "timeline", or "what happened with".
name: mem-history
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Project Memory Search

Query cross-session history via claude-mem.

**Scope**: Searches observations stored by claude-mem in the current project only. Does not access git history, file contents, or observations from other projects.

**If claude-mem tools are not available**: Tell the user that cross-session memory requires the claude-mem plugin (`/plugin install claude-mem@thedotmack`). Suggest alternatives: check `git log` for recent changes, read CLAUDE.md files for project context, or use `git blame` for file history.

## 3-Layer Workflow

1. **Search** (index): `search` with keywords — returns compact list with IDs (~50-100 tokens/result)
2. **Get details**: `get_observations` with IDs from search — returns full narratives (~500-1000 tokens/result)
3. **Timeline**: `timeline` with anchor ID or query — shows chronological context around an observation

## When to Use

| Scenario                        | Action                                            |
| ------------------------------- | ------------------------------------------------- |
| "What did we fix last session?" | `search` with file path or feature name           |
| "Did we try this before?"       | `search` with approach keywords                   |
| Past decisions on a feature     | `search` → `get_observations` on relevant IDs     |
| Recurring bug investigation     | `search` type filter for gotchas/problem-solution |
| Full project timeline           | `timeline` with broad query                       |

## Search Tips

- Use FTS5 syntax: `AND`, `OR`, `NOT`, quoted phrases
- Filter by type: `gotcha`, `problem-solution`, `decision`, `discovery`
- Filter by file path for file-specific history
- Start with small limits (5-10), expand if needed

## Output

Present findings as a concise list ordered by recency:

```
MEMORY RESULTS: {query}
=======================
[date] {type} — {summary} (ID: {id})
[date] {type} — {summary} (ID: {id})

If nothing found: "No observations found for '{query}'. Try broader terms or check git log."
```
