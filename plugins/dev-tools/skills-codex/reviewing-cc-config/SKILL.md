---
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash(wc *)
argument-hint: "[skills|agents|hooks|claude-md|commands|all] [--fix]"
description:
  Review Claude Code configuration for context efficiency, signal density,
  and anti-patterns. Use when user says "review config", "review setup", "check configuration",
  "review cc config", "context review", "config review", "review my setup", "review
  skills", "review agents", "review hooks", or wants feedback on their Claude Code
  configuration quality.
name: reviewing-cc-config
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

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

Read the first match. If no match found, **stop and warn the user** that
RUBRIC.md is missing — do not proceed without the rubric.

**Parse `$ARGUMENTS`:**

- No args or `all` → review everything
- `skills` → review only skills
- `agents` → review only agents
- `hooks` → review only hooks
- `claude-md` → review only CLAUDE.md files
- `commands` → review only commands
- `--fix` → apply fixes after review (Phase 5)

### Spawn review agents (ALL in ONE message)

Read `RUBRIC.md` (co-located with this skill) first. Pass relevant rule IDs
to each agent. Spawn up to 4 agents in parallel, one per component type.
Skip agents for component types not present or not in scope.

Each agent prompt must include:

1. The agent's role and component type
2. The list of files to review
3. The relevant rules from RUBRIC.md (paste the rule IDs and one-line checks)
4. The output format specified below

**Agent 1: CLAUDE.md Reviewer** — Rules: SD-CLAUDE-MD, AR-HOOK-DETERMINISTIC,
AR-SKILL-DEMAND, AP-OVER-SPECIFIED (>150 lines), CB-STARTUP (<3K tokens).
Output per file: `### path (lines, ~tokens)` + rule/verdict/notes table.
Keep under 1500 tokens.

**Agent 2: Skills Reviewer** — Rules: SD-DESCRIPTION, CB-FORK, SD-TOOL-MINIMAL,
AR-VERIFY, AR-MODEL-MATCH, AP-TRIGGER-OVERLAP, AP-OVER-SPECIFIED (>200 lines),
CB-PROGRESSIVE. Output per skill: `### name (model, invocable, lines)` +
rule/verdict/notes table + trigger overlap matrix (conflicts only).
Keep under 2000 tokens.

**Agent 3: Agents & Commands Reviewer** — Rules: AR-ISOLATION, SD-TOOL-MINIMAL,
SD-RETURN, AP-SCOPE-UNBOUNDED, AR-MODEL-MATCH, AP-OVER-SPECIFIED (>100 lines).
Output per agent/command: `### name (model, tools, lines)` +
rule/verdict/notes table. Keep under 1500 tokens.

**Agent 4: Hooks Reviewer** — Rules: AR-HOOK-DETERMINISTIC, plus: performance
(<2s), exit code discipline (0=context, 2=blocking), event appropriateness
(PreToolUse=validation, PostToolUse=verification, SessionStart=setup,
Notification=alerts, PostCompact=metrics). Output per hook:
`### name (event, lines)` + check/verdict/notes table. Keep under 1000 tokens.

---

## Phase 4: Aggregate, Cross-Check & Present

Collect results from all review agents. **Cross-check**: for each ERROR
finding that references a specific line number or file path, verify it
exists by reading the actual file. Agents can hallucinate line numbers —
drop findings that don't match reality. Present:

Report structure:

1. **Context Budget** table: component / count / token est / rating (LEAN/OK/HEAVY/BLOATED)
2. **Findings by Severity**: ERRORS (must fix), WARNINGS (should fix), INFO (consider)
   - One sentence per finding, no preamble. State what IS wrong. Include component names, line numbers, token counts
3. **Cross-Cutting**: trigger overlap matrix, model routing summary, hook vs CLAUDE.md balance
4. **Top 5 Highest-Impact Improvements** with estimated savings
5. **What's Working Well** — explicit acknowledgment of good patterns

---

## Phase 5: Apply Fixes (only if `--fix` in arguments)

**Skip this phase entirely unless `--fix` is in `$ARGUMENTS`.**

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

## Examples

```
/reviewing-cc-config                    # Review all config components
/reviewing-cc-config skills             # Review only skills
/reviewing-cc-config claude-md          # Review only CLAUDE.md files
/reviewing-cc-config hooks agents       # Review hooks and agents
/reviewing-cc-config all --fix          # Review everything, then apply fixes
```

**Execute this workflow now.**
