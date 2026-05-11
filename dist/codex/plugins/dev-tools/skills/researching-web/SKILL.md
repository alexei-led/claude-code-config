---
description: Web research via Pi web providers. Use for technical comparisons, recent
  facts, best practices, standards, pros and cons, or questions needing grounded web
  evidence.
name: researching-web
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Web Research in Pi

Use Pi's Perplexity-backed tools:

- `web_search` for source discovery.
- `web_answer` for focused factual questions.
- `web_research` for broad or multi-step investigations.

## Boundaries

Use this for:

- comparisons and trade-offs
- recent facts and release behavior
- standards and external best practices
- vendor docs or public evidence

Do not use web tools for private code, secrets, credentials, proprietary data,
or local code exploration. Use local search first for repo-specific questions.

## Workflow

1. Restate the research question and decide if it is simple or broad.
2. For simple factual questions, use `web_answer` with a focused query.
3. For source selection, use `web_search`, then cite the best official or
   primary sources from the returned results.
4. For broad investigations, use `web_research` and tell the user the report
   will arrive asynchronously.
5. Compare claims against local project constraints before recommending changes.
6. Report uncertainty and source gaps directly.

## Output Contract

```markdown
## Research Result

### Answer

<concise answer>

### Evidence

- <source title/url or grounded result> — <why it matters>

### Fit For This Repo

<what changes because of local constraints>

### Gaps

<any missing evidence>
```
