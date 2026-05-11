---
description:
  Current library documentation via the ctx7 CLI. Use when the user mentions
  "ctx7" or "context7", asks for API docs, syntax, code examples, versioned library
  behavior, or needs docs lookup without provider-specific tools.
name: context7-cli
---

# Context7 CLI Documentation Lookup

Use `ctx7` for narrow library/framework/API documentation. This skill is the
portable docs lookup path for Claude, Codex, Gemini, Pi, and AGENTS.md-style
agents.

## Scope

Use this skill for:

- API signatures, options, config keys, and syntax.
- Library or framework examples grounded in current docs.
- Version-specific behavior when the requested version is known.
- Checking docs before writing code when training data may be stale.

Do not use this skill as the primary workflow for:

- Comparisons, recommendations, market research, or broad best-practice surveys.
- Debugging private production payloads.
- Queries that would require sending secrets, credentials, personal data, or
  proprietary code outside the project.

Route broad research to the repo's web research skill. Use docs lookup later for
chosen-library syntax.

## Required Workflow

You MUST follow these steps and SHOW the exact `ctx7` commands you ran in the
response. Claims like "I used Context7" without an emitted command do not
satisfy this skill.

1. Identify the library and version from project files (`package.json`,
   `go.mod`, `pyproject.toml`, `requirements.txt`, lockfiles). State the
   identified version, or say version is unknown.
2. Build a query from the user's real topic. Do not use one-word placeholders.
3. If the user provided `/org/project` or `/org/project/version`, skip step 4
   and call `ctx7 docs` directly with that ID.
4. Otherwise resolve the library ID first by running and showing:

   ```bash
   ctx7 library <name> "<specific query>"
   ```

5. Select the best library ID from the results and explain why.
6. Fetch docs by running and showing:

   ```bash
   ctx7 docs /org/project "<specific query>"
   ```

7. Ground the answer in the returned docs. Quote only the relevant parts.
8. If `ctx7` is missing on `PATH`, retry with the `npx` (or `bunx`) fallback
   and say so:

   ```bash
   npx ctx7@latest library <name> "<specific query>"
   npx ctx7@latest docs /org/project "<specific query>"

   # or, if you use Bun:
   bunx ctx7@latest library <name> "<specific query>"
   bunx ctx7@latest docs /org/project "<specific query>"
   ```

9. If Context7 has no useful match, use available web tools such as
   `web_search` or `web_answer` for official docs, release notes, or focused
   factual fallback. Say that a fallback was used.

## Hard Limits

- Do not include secrets, credentials, private payloads, personal data, or
  proprietary code in any query.
- Always pass a real query to both commands.
- Do not call `ctx7 library` more than 3 times for one user question.
- Do not call `ctx7 docs` more than 3 times for one user question.
- Prefer `ctx7 docs --json` when structured output will reduce ambiguity.
- If docs remain insufficient after the limit, report the gap and use the best
  available fallback.

## Response Contract

For docs lookup results, return:

1. Library/version identified, or say version is unknown.
2. Library ID selected and why.
3. Concise syntax or example guidance grounded in docs.
4. Fallback source used, if any.
5. Boundary note when the user is asking for comparison or broad research.

## References

- [Documentation commands](references/docs.md)
- [Skill commands](references/skills.md)
- [CLI setup](references/setup.md)
