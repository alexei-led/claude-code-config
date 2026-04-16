---
description: Implementation process discipline for all languages — surface assumptions
  before coding, define verifiable success criteria, plan before writing. Use when
  implementing features, writing functions/classes/modules, or adding new code in
  any language. Complements language-specific skills (writing-go, writing-python,
  etc.) with process guardrails.
name: coding
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Coding Process Discipline

## Before Writing Code

**State your assumptions. Don't pick an interpretation silently.**

- If the request is ambiguous, name the interpretations and ask — one clarifying question beats one wrong implementation.
- If something is unclear, stop. Name what's confusing. Ask.
- If a simpler approach exists than what was asked, say so before proceeding.

## Define Success Criteria First

**Transform the task into verifiable goals before starting.**

| Vague            | Verifiable                                          |
| ---------------- | --------------------------------------------------- |
| "Add validation" | Write tests for invalid inputs, then make them pass |
| "Fix the bug"    | Write a test that reproduces it, then make it pass  |
| "Refactor X"     | Tests pass before and after, diff is minimal        |

For multi-step work, state a brief plan upfront:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## During Implementation

**Every changed line must trace directly to the request.**

When done, check: does the diff contain anything the user didn't ask for? If yes, remove it.
