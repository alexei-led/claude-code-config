---
description: ctx7 (Context7) CLI mechanics for querying versioned library documentation.
  Use when the user mentions "ctx7" or "context7", passes a `/org/project` library
  ID, or another skill needs the exact ctx7 command workflow. NOT the docs-lookup
  decision flow or web fallback — that is looking-up-docs.
name: context7-cli
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# Context7 CLI Mechanics

Reference for driving the `ctx7` CLI: resolve a library name to an ID, then
query docs with that ID. This skill is tool mechanics only. The docs-lookup
decision flow and tool fallback chain live in `looking-up-docs`; this skill is
Tier 1 of that chain.

## Scope

Use this skill for:

- The exact `ctx7 library` / `ctx7 docs` command workflow and selection rules.
- Library-ID resolution and version-specific docs queries.
- The `npx` / `bunx` fallback when `ctx7` is not installed.

Do not use this skill for:

- Deciding when to fall back from Context7 to web search — that is
  `looking-up-docs`.
- Comparisons, recommendations, or broad research — that is `researching-web`.
- Queries that would send secrets, credentials, personal data, or proprietary
  code outside the project.

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

9. If Context7 has no useful match after one rephrase and one alternate
   library name, report that Context7 was exhausted. Escalation to web tools
   is owned by `looking-up-docs` (Tier 2 onward), not this skill.

## Hard Limits

- Do not include secrets, credentials, private payloads, personal data, or
  proprietary code in any query.
- Always pass a real query to both commands.
- Do not call `ctx7 library` more than 3 times for one user question.
- Do not call `ctx7 docs` more than 3 times for one user question.
- Prefer `ctx7 docs --json` when structured output will reduce ambiguity.
- If docs remain insufficient after the limit, report the gap and hand back to
  `looking-up-docs` for the next tier.

## Response Contract

For ctx7 results, return:

1. Library/version identified, or say version is unknown.
2. Library ID selected and why.
3. Concise syntax or example guidance grounded in docs.
4. Whether the `npx`/`bunx` fallback was used.
5. Whether Context7 was exhausted (hand-off to `looking-up-docs`).

## Failure Cases

- `ctx7 library` returns no match: try a shorter or alternate name once; if
  still no match, report Context7 exhausted and hand back to `looking-up-docs`.
- Docs returned are clearly outdated (version mismatch): note the discrepancy,
  state the version found vs the version needed, and hand back to
  `looking-up-docs` for the next tier.
