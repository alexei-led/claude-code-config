---
description: >
  Review and score AI agent/skill instructions for quality across 8 dimensions: signal density,
  scope specificity, output structure, format efficiency, failure handling, grounding discipline,
  routing precision, and progressive disclosure. Use when authoring, reviewing, or improving
  SKILL.md, AGENT.md, AGENTS.md, or CLAUDE.md files; when asked to "lint", "audit", "review",
  or "score" prompts or instructions; when checking instruction quality for a specific AI model
  or generically; when working on plugin agent/skill definitions; or any time the user is
  editing or creating instruction files for AI coding agents.
name: reviewing-instructions
---

# Instruction Review

Review AI agent and skill instruction files for quality. Combines a fast structural pre-pass with model-aware semantic scoring across 8 dimensions (0–10 each). Do not fabricate findings — cite exact file/section or missing evidence for every issue.

## Accepted Inputs

The user may pass:

- A file path or plugin name to scope the review (omitted → review all plugins)
- `--model <name>` to override model-specific rule selection (e.g. `--model claude`, `--model gemini`, `--model openai`)
- Plugin name without path separator → expand to `src/plugins/<name>/`

## Model Context Resolution

For each instruction file under review:

1. Check `--model` arg first; if absent, check the file's frontmatter `model:` field. Args take precedence.
2. Look for `references/models/<model>.md` in this skill's directory. Read it if present.
3. If no local reference: WebFetch the model's official prompting guide:
   - Claude: `https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview`
   - GPT series: `https://platform.openai.com/docs/guides/prompt-engineering`
   - Gemini: `https://ai.google.dev/gemini-api/docs/prompting-strategies`
   - Other: web search for `<model> prompting guide best practices`
4. If no model anywhere: read `references/models/generic.md`.

Surface the resolution as a one-line header in the report: `Model context: claude (from frontmatter)`.

## Step 1: Structural Pre-Pass

```bash
uv run python src/skills/reviewing-instructions/scripts/lint-instructions.py
```

Record which rule IDs flagged (U-SCOPE, K-DESC, F-NO-TABLE, etc.). The semantic review below is authoritative — this is a heuristic baseline.

## Step 2: Semantic Review and Scoring

Read `references/scoring-rubric.md` for 0–10 anchors and weights per dimension.

For each file:

1. Read it fully.
2. Identify model from frontmatter (if any) and load model context per resolution above.
3. Score each of the 8 dimensions 0–10 with a one-line justification.
4. Rate each applicable lint rule PASS / WARN / FAIL. For WARN/FAIL: cite exact section and propose a concrete fix.
5. Compute weighted overall score (weights in `references/scoring-rubric.md`).
6. List top 3 improvements by impact.

## Output

```
## Instruction Review Report

### Summary
- Files reviewed: N (model: M or generic)
- Structural pre-pass: N errors, N warnings (or: skipped)
- Scores: mean X.X / 10 (range Y.Y–Z.Z)

### Scores

path/to/SKILL.md — overall 7.8 / 10
  Signal Density: 8 — most lines carry actionable constraints
  Scope Specificity: 6 — positive scope only; no exclusions stated
  Output Structure: 9 — template present with required fields
  Format Efficiency: 10 — no tables/diagrams/italic; clean
  Failure Handling: 5 — one failure case; missing exit conditions
  Grounding Discipline: 7 — grounding required in key steps
  Routing Precision: 8 — trigger phrases present; minor K-DESC gap
  Progressive Disclosure: 7 — 180 lines; borderline; consider splitting

### Critical Findings (FAIL)
1. path — U-SCOPE: no scope boundary. Fix: add "Do not X; review only Y."

### Top Improvements (by impact)
1. ...

### Per-File Detail
...
```
