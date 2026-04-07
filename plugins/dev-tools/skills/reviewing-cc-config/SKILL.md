---
name: reviewing-cc-config
description: >-
  Review Claude Code configuration for context efficiency, signal density, and
  anti-patterns. Use when user says "review config", "review setup", "check
  configuration", "review cc config", "context review", "config review",
  "review my setup", "review skills", "review agents", "review hooks",
  or wants feedback on their Claude Code configuration quality.
user-invocable: true
context: fork
model: opus
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash(wc *)
  - Agent
  - AskUserQuestion
  - TaskCreate
  - TaskUpdate
argument-hint: "[skills|agents|hooks|claude-md|commands|all] [--fix]"
---

# Claude Code Configuration Review

Review configuration against context engineering principles derived from
Anthropic's "Effective Context Engineering for AI Agents" and
"Best Practices for Claude Code."

**Use TaskCreate** to track these 4 phases:

1. Discover and inventory configuration
2. Measure context budget impact
3. Review against rubric (parallel agents)
4. Aggregate and present findings

---

## Phase 1: Discovery

Scan for all Claude Code configuration components. Check BOTH standard layout
and plugin layout (cc-thingz style).

### Standard layout

```bash
# Glob these patterns in parallel
CLAUDE.md
CLAUDE.local.md
.claude/CLAUDE.md
.claude/settings.json
.claude/settings.local.json
.claude/skills/*/SKILL.md
.claude/agents/*.md
.claude/commands/**/*.md
# Also check parent dirs (monorepo) and home
~/.claude/CLAUDE.md
../CLAUDE.md
```

### Plugin layout (if `plugins/` or `.claude-plugin/` exists)

```bash
plugins/*/skills/*/SKILL.md
plugins/*/agents/**/*.md
plugins/*/hooks/*.sh
plugins/*/commands/**/*.md
.claude-plugin/marketplace.json
```

### Hooks and MCP servers

Extract hook script paths from settings.json `hooks` field. Read each script.
Extract MCP server names from settings.json `mcpServers` field. Count them.

Build inventory table:

```markdown
| Component   | Count | Token Est | Details                |
| ----------- | ----- | --------- | ---------------------- |
| CLAUDE.md   | N     | ~Nt       | paths                  |
| Skills      | N     | ~Nt       | names (auto/invocable) |
| Agents      | N     | ~Nt       | names (model)          |
| Hooks       | N     | ~Nt       | events                 |
| Commands    | N     | ~Nt       | names                  |
| MCP servers | N     | —         | names                  |
```

Token estimation: `word_count * 1.3` for English text.

---

## Phase 2: Context Budget Measurement

Calculate the **session startup cost** — tokens loaded before the user's
first prompt:

```
Startup Budget = CLAUDE.md tokens
               + auto-activated skill bodies (skills without user-invocable: true
                 that match common prompts)
               + hook startup output (SessionStart hooks)
               + settings overhead
```

### Thresholds

| Budget     | Rating  | Action                                |
| ---------- | ------- | ------------------------------------- |
| <2K tokens | LEAN    | Ideal — maximum attention available   |
| 2K-4K      | OK      | Acceptable for complex projects       |
| 4K-6K      | HEAVY   | Consider moving content to skills     |
| >6K        | BLOATED | Urgent — context rot risk from turn 1 |

Count CLAUDE.md lines and estimate tokens. Flag if CLAUDE.md exceeds 150
lines or ~3K tokens.

---

## Phase 3: Review Against Rubric

Find and read the rubric (co-located with this skill):

```bash
# Try both plugin layout and standard layout
Glob("**/skills/reviewing-cc-config/RUBRIC.md")
```

Read the first match. If no match found, use the fallback rules table
at the end of this skill.

**Parse `$ARGUMENTS`:**

- No args or `all` → review everything
- `skills` → review only skills
- `agents` → review only agents
- `hooks` → review only hooks
- `claude-md` → review only CLAUDE.md files
- `commands` → review only commands
- `--fix` → apply fixes after review (Phase 5)

### Spawn review agents (ALL in ONE message)

Spawn up to 4 agents in parallel, one per component type. Skip agents for
component types not present or not in scope.

**Agent 1: CLAUDE.md Reviewer**

```
You are reviewing Claude Code CLAUDE.md files for context efficiency.

## Rules to apply

### SD-CLAUDE-MD (error): Non-derivable instructions only
Each line must pass: "Would removing this cause Claude to make mistakes?"
Flag: standard conventions Claude already knows, self-evident practices,
file-by-file descriptions, long tutorials, information derivable from code.

### AR-HOOK-DETERMINISTIC (error): Deterministic rules belong in hooks
Flag: rules requiring 100% enforcement (linting, formatting, file protection)
that are in CLAUDE.md instead of hooks.

### AR-SKILL-DEMAND (warning): Domain knowledge belongs in skills
Flag: domain-specific workflows or specialized knowledge in CLAUDE.md that
loads every session but is only relevant sometimes.

### AP-OVER-SPECIFIED (warning): Length check
Flag if >150 lines. Count non-empty, non-comment lines.

### CB-STARTUP (warning): Token budget
Estimate tokens (words * 1.3). Flag if >3K tokens.

## Files to review
[list CLAUDE.md file paths]

## Output format
For each file:
### `<path>` (<line_count> lines, ~<token_est> tokens)
| Rule | Verdict | Line(s) | Notes |
|------|---------|---------|-------|

Then: specific lines to cut, move to hooks, or move to skills.
Keep output under 1500 tokens.
```

**Agent 2: Skills Reviewer**

```
You are reviewing Claude Code skill definitions for context efficiency
and routing precision.

## Rules to apply

### SD-DESCRIPTION (error): Precise routing signals
Description must have specific trigger phrases. Flag generic descriptions
or missing triggers.

### CB-FORK (error): Context isolation
Skills with Read/Glob/Grep in allowed-tools MUST have `context: fork`.
Exception: skills reading only 1-2 specific files.

### SD-TOOL-MINIMAL (warning): Minimal tool lists
Flag tools in allowed-tools that are never referenced in the skill body.

### AR-VERIFY (error): Self-verification
Skills producing code/config must include a verification step.

### AR-MODEL-MATCH (warning): Model assignment
opus = complex reasoning. sonnet = standard work. haiku = lightweight.
Flag mismatches.

### AP-TRIGGER-OVERLAP (error): Trigger uniqueness
Compare descriptions across ALL skills. Flag any two skills whose trigger
phrases would match the same user prompt.

### AP-OVER-SPECIFIED (warning): Length check
Flag skills >200 lines.

### CB-PROGRESSIVE (info): Runtime discovery
Note skills that hardcode file paths vs using Glob/Grep at runtime.

## Files to review
[list skill SKILL.md paths]

## Output format
For each skill:
### `<name>` (model: <model>, invocable: <bool>, <line_count> lines)
| Rule | Verdict | Notes |
|------|---------|-------|

Then: trigger overlap matrix (only conflicts), top 5 improvements.
Keep output under 2000 tokens.
```

**Agent 3: Agents & Commands Reviewer**

```
You are reviewing Claude Code agent and command definitions for
context efficiency and architectural quality.

## Rules to apply

### AR-ISOLATION (warning): Single responsibility
Each agent should address one concern. Flag agents mixing multiple
unrelated responsibilities.

### SD-TOOL-MINIMAL (warning): Minimal tool lists
Flag tools never referenced in the agent body.

### SD-RETURN (warning): Condensed output format
Agent must specify expected output format. Flag agents without
output format section.

### AP-SCOPE-UNBOUNDED (error): Scope boundaries
Agents must have explicit scope limits. Flag agents without
"ONLY", "Do not", "exclusively", or clear stopping conditions.

### AR-MODEL-MATCH (warning): Model assignment
Check model tier matches task complexity.

### AP-OVER-SPECIFIED (warning): Length check
Flag agents >100 lines.

## Files to review
[list agent .md and command .md paths]

## Output format
For each agent/command:
### `<name>` (model: <model>, tools: <count>, <line_count> lines)
| Rule | Verdict | Notes |
|------|---------|-------|

Then: top 5 improvements.
Keep output under 1500 tokens.
```

**Agent 4: Hooks Reviewer**

```
You are reviewing Claude Code hook scripts for correctness and
architectural fitness.

## Rules to apply

### AR-HOOK-DETERMINISTIC (error): Only deterministic actions
Hooks must perform deterministic, unconditional actions.
Flag hooks that contain conditional logic better suited for
CLAUDE.md advisory instructions.

### Performance: Hooks run on EVERY tool call
Flag: network calls, slow operations, large file reads.
Hooks must be fast (<2s).

### Error handling: Exit codes
Exit 0 = success (output shown as context).
Exit 2 = blocking (stderr sent to Claude for fixing).
Other = silent failure.
Flag: missing exit code handling, swallowed errors.

### Event appropriateness
Check hook event matches the action:
- PreToolUse: validation/blocking before action
- PostToolUse: verification/linting after action
- SessionStart: environment setup
- Notification: user alerts
- PostCompact: metrics/cleanup
Flag mismatched events.

## Files to review
[list hook script paths + settings.json hook config]

## Output format
For each hook:
### `<name>` (event: <event>, <line_count> lines)
| Check | Verdict | Notes |
|-------|---------|-------|

Then: performance concerns, top improvements.
Keep output under 1000 tokens.
```

---

## Phase 4: Aggregate & Present

Collect results from all review agents. Present:

```markdown
## Configuration Review Report

**Project**: {name}
**Date**: {date}
**Rubric**: Context Engineering Review Rubric (16 rules)

### Context Budget

| Component   | Count | Token Est       | Rating                |
| ----------- | ----- | --------------- | --------------------- |
| CLAUDE.md   | N     | ~Nt             | LEAN/OK/HEAVY/BLOATED |
| Skills      | N     | ~Nt (auto only) | —                     |
| Hooks       | N     | ~Nt (startup)   | —                     |
| **Startup** | —     | **~Nt**         | **{rating}**          |

---

### Findings by Severity

#### ERRORS (Must Fix)

- [{rule}] `component` — Issue. Fix.

#### WARNINGS (Should Fix)

- [{rule}] `component` — Issue. Fix.

#### INFO (Consider)

- [{rule}] `component` — Observation.

---

### Cross-Cutting Analysis

- **Trigger overlap matrix**: {any conflicts between skills}
- **Model routing summary**: {opus/sonnet/haiku distribution and fitness}
- **Hook vs CLAUDE.md balance**: {deterministic rules in right place?}
- **Progressive disclosure**: {upfront vs runtime loading ratio}

### Top 5 Highest-Impact Improvements

1. {improvement} — {estimated token savings or quality gain}
2. ...

### What's Working Well

- {explicit acknowledgment of good patterns}
```

### Writing Style

- One sentence per finding. No preamble
- State what IS wrong, not "consider" or "might"
- Include component names, line numbers, token counts
- Lead with impact: "Saves ~500 tokens/session" or "Prevents mis-routing"

---

## Phase 5: Apply Fixes (only if `--fix` in arguments)

**Skip this phase entirely unless `--fix` is in `$ARGUMENTS`.**

<!-- CC-ONLY: begin -->

If `--fix` is NOT present, use `AskUserQuestion`:

| Header | Question                     | Options                                                         |
| ------ | ---------------------------- | --------------------------------------------------------------- |
| Action | Apply fixes from the review? | Fix all errors / Fix errors + warnings / Show diffs only / Skip |

<!-- CC-ONLY: end -->

Apply only approved fixes:

1. **CLAUDE.md**: Remove flagged lines, move content to skills/hooks
2. **Skills**: Add missing `context: fork`, trim tool lists, fix descriptions
3. **Agents**: Add scope boundaries, output format sections
4. **Hooks**: Fix exit codes, event assignments

After each fix, show the diff. Do NOT make changes beyond what was flagged.

**Post-fix verification**: After all fixes are applied, re-check modified
components against the rules that triggered the fix. Confirm each finding
is resolved. Report any regressions.

---

## Fallback Rules (if RUBRIC.md not found)

If the Glob for `RUBRIC.md` returns no results, apply these core rules:

| Rule                  | Severity | Check                                          |
| --------------------- | -------- | ---------------------------------------------- |
| CB-STARTUP            | warning  | Startup tokens <4K                             |
| CB-FORK               | error    | File-reading skills use `context: fork`        |
| SD-CLAUDE-MD          | error    | CLAUDE.md: only non-derivable instructions     |
| SD-DESCRIPTION        | error    | Precise trigger phrases in descriptions        |
| SD-TOOL-MINIMAL       | warning  | No unused tools in allowed-tools               |
| AR-HOOK-DETERMINISTIC | error    | Deterministic rules in hooks, not CLAUDE.md    |
| AR-VERIFY             | error    | Code-producing skills have verification        |
| AP-TRIGGER-OVERLAP    | error    | No ambiguous trigger overlap between skills    |
| AP-SCOPE-UNBOUNDED    | error    | Agents have explicit scope limits              |
| AP-OVER-SPECIFIED     | warning  | CLAUDE.md <150 lines, skills <200, agents <100 |

---

## Examples

```
/reviewing-cc-config                    # Review all config components
/reviewing-cc-config skills             # Review only skills
/reviewing-cc-config claude-md          # Review only CLAUDE.md files
/reviewing-cc-config hooks agents       # Review hooks and agents
/reviewing-cc-config all --fix          # Review everything, then apply fixes
```

**Execute this workflow now.**
