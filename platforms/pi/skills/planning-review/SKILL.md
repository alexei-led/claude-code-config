---
name: planning-review
description: Review implementation plans in docs/plans/ for correctness, scope, testing, and over-engineering. Use when user asks to review a plan before coding or validate plan quality.
---

# Planning Review

Review a plan file. Read-only unless the user explicitly asks for edits after the review.

## Inputs

Use the plan path from the user. If missing:
- list `docs/plans/*.md`
- exclude `docs/plans/completed/`
- if one plan exists, use it
- if several exist, ask which one with `ask_user_question`

## Context Loading

Before reviewing:
1. Read the plan.
2. Read `CLAUDE.md`, `AGENTS.md`, or equivalent project guidance if present.
3. Read 1-3 relevant code files named in the plan to verify the plan fits reality.
4. Load custom rules with:

```bash
bash ../planning-common/scripts/resolve-rules.sh planning-rules.md
```

Apply custom rules as extra review criteria.

For broad plans, spawn one bounded background `reviewer` or `planner` agent for an independent pass, then verify its claims yourself:

```text
Agent({
  subagent_type: "planner",
  description: "Review plan fit",
  run_in_background: true,
  prompt: "Review <plan path> against current code. Return only blockers, missing tasks, and over-engineering. Do not edit."
})
```

Use web tools only when the plan depends on external APIs, standards, or migration guidance.

## Review Checklist

### Critical
- Problem is stated clearly.
- Proposed solution actually solves it.
- Missing steps do not exist.
- Edge cases are covered.
- Testing is explicit for each task.

### Scope
- No unrelated work.
- No scope creep hidden as cleanup.
- Task ordering makes sense.
- Dependencies are acknowledged.

### Simplicity
- No speculative abstractions.
- No "future-proofing" garbage without a real need.
- No split into layers that add ceremony but no value.
- Simpler path noted when one exists.

### Task Quality
- One logical unit per task.
- Specific task names.
- File lists present.
- Tests are separate checklist items.
- Verification step exists before completion.

### Conventions
- Matches project rules and existing patterns.
- Respects testing style and tooling.
- Avoids naming or structure that conflicts with current code.

## Output Format

Report problems only.

If `structured_output` is available, use it for the final verdict and prioritized fixes.

```markdown
## Plan Review

### CRITICAL
- `[plan-review]` Section or task — issue. Fix.

### IMPORTANT
- `[plan-review]` Section or task — issue. Fix.

### MINOR
- `[plan-review]` Section or task — issue. Fix.

### Verdict
- APPROVE
- NEEDS REVISION
```

Rules:
- Tag every finding with `[plan-review]`.
- Cite the section or task.
- State the problem, why it matters, and the fix.
- No praise. No filler. No fake balance.

## If User Wants Revisions

After review, if the user asks to fix the plan:
1. edit the plan directly
2. preserve existing structure unless it is wrong
3. re-run a brief self-review against the checklist
