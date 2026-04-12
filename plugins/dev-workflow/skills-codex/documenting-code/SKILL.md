---
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
description:
  Update project documentation based on recent changes. Use when user says
  "update docs", "document", "add documentation", "update readme", "write docs", or
  wants to improve documentation.
name: documenting-code
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Documentation Update

Update project documentation to reflect current code state.

1. Determine documentation scope
2. Analyze recent changes
3. Spawn docs-keeper agent
4. Update documentation
5. Verify and report

---

## Phase 1: Determine Scope

Use AskUserQuestion:

| Header    | Question                            | Options                                                                                                                                                                                                        |
| --------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Doc scope | What documentation should I update? | 1. **Auto-detect** - Scan for outdated docs based on recent changes 2. **README** - Update project README 3. **API docs** - Update API/function documentation 4. **All** - Comprehensive documentation refresh |

## Phase 2-4: Spawn docs-keeper Agent

Spawn **docs-keeper** agent with documentation prompt:

## Phase 4: Research Best Practices (If Needed)

Use Context7 for documentation patterns:

```
mcp__context7__query-docs for GoDoc, Sphinx, or framework-specific docs
```

## Phase 5: Verify and Present Summary

**Independent verification** (do not trust the agent's self-report):

1. Run `git diff --stat` to confirm files were actually changed
2. For each changed file, verify the diff looks correct (no broken links, no placeholder text)
3. If no files changed, report that docs-keeper made no modifications

Report what was updated, verified diffs, and any issues found.

If no recent changes are found or documentation scope is unclear, ask the user what to document rather than generating speculative documentation.

**Execute documentation update now.**
