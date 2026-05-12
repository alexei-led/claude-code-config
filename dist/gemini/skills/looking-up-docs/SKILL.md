---
description: Compatibility router for library documentation lookup. Use when user
  says "look up docs", "how to use", "API for", "syntax for", "examples of", "show
  me the docs", or needs API references, code examples, or framework-specific documentation.
  Routes to the context7-cli workflow.
name: looking-up-docs
---

# Documentation Lookup Router

Thin router: preserve `looking-up-docs` trigger, delegate all work to `context7-cli`. Do not maintain a parallel docs lookup flow here.

## Route

Use the `context7-cli` workflow for narrow docs lookup. SHOW the exact `ctx7`
commands you ran in the response — claiming "I used Context7" without
emitting a command does not satisfy this skill.

1. Identify the library and version from project files (`package.json`,
   `go.mod`, `pyproject.toml`, lockfiles). State the version or say it is
   unknown.
2. Unless the user already supplied `/org/project` or `/org/project/version`,
   resolve a library ID by running and showing:

   ```bash
   ctx7 library <name> "<specific query>"
   ```

3. Query docs with a real topic by running and showing:

   ```bash
   ctx7 docs /org/project "<specific query>"
   ```

4. Ground syntax and examples in returned docs.
5. If `ctx7` is missing on `PATH`, fall back to `npx` (or `bunx`) for both
   `library` and `docs` invocations and say a fallback was used:

   ```bash
   npx ctx7@latest library <name> "<specific query>"
   npx ctx7@latest docs /org/project "<specific query>"

   # or, if you use Bun:
   bunx ctx7@latest library <name> "<specific query>"
   bunx ctx7@latest docs /org/project "<specific query>"
   ```

6. Use web tools such as `web_search` or `web_answer` only when Context7 has
   no useful match, and say a fallback was used.

## Boundaries

Use this skill for:

- API docs, syntax, config keys, and examples.
- Version-specific library behavior.
- Documentation checks before writing code.

Do not use this skill as the primary workflow for:

- Comparisons, recommendations, pros/cons, or market research.
- Broad best-practice surveys.
- Recent ecosystem news.

Route those to `researching-web`; use docs lookup later for exact syntax in the
chosen library.

## Safety Rules

- Do not include secrets, credentials, personal data, private payloads, or
  proprietary code in ctx7 queries.
- Do not call `ctx7 library` more than 3 times for one question.
- Do not call `ctx7 docs` more than 3 times for one question.
- Always pass a real query, not a placeholder.
- Prefer `ctx7 docs --json` when structured output helps.

## Response Contract

When answering a docs lookup, report:

1. Library/version identified, or say version is unknown.
2. Library ID selected.
3. Concise syntax/example guidance grounded in docs.
4. Fallback used, if any.
5. Boundary note if the request is actually research or comparison.

If the user asks to describe the workflow, describe these steps instead of
answering from memory.
