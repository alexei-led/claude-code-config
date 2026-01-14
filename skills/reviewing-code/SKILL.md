---
name: reviewing-code
description: Multi-agent code review for security, quality, and architecture. Use when user says "review", "review code", "check code", "code review", "review my changes", "review this", or wants feedback on their code.
user-invocable: true
allowed-tools:
  - Task
  - TodoWrite
  - AskUserQuestion
  - Bash
argument-hint: [deep] [external]
---

# Multi-Agent Code Review

**Use TodoWrite** to track these 4 phases:

1. Detect languages and scope
2. Spawn review agents
3. Collect agent results
4. Aggregate and present findings

---

**Parse `$ARGUMENTS`:**

- `deep` → 6-12 specialized Claude sub-agents (language-specific reviewers)
- `external` → Add external AI reviewers (Codex + Gemini). **Only if explicitly requested.**

**IMPORTANT:** Without `external` flag, run ONLY Claude agents. Never run Codex or Gemini unless `external` is in arguments.

| Arguments     | Claude Agents                                                       | External (Codex + Gemini) |
| ------------- | ------------------------------------------------------------------- | ------------------------- |
| (none)        | go-engineer, python-engineer                                        | ❌ No                     |
| deep          | go-qa, go-idioms, go-tests, go-impl, go-docs, go-simplify (+ py-\*) | ❌ No                     |
| external      | go-engineer, python-engineer                                        | ✅ Yes                    |
| deep external | All 6-12 specialized sub-agents                                     | ✅ Yes                    |

---

## Step 1: Detect Language & Ask Scope

Detect languages in changes:

```bash
git diff --name-only HEAD | grep -E '\.(go|py|ts|tsx|html|css|js)$' | head -20
```

Then use AskUserQuestion:

| Header       | Question                   | Options                                                                                                                                |
| ------------ | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Review scope | What code should I review? | 1. **Uncommitted changes** - git diff HEAD 2. **Branch vs master** - git diff master...HEAD 3. **Specific files** - I'll provide paths |

Build git command based on choice.

---

## Step 2: Spawn Agents (ALL in ONE message)

### Default Mode: Language Engineers

For each detected language, spawn ONE Task:

- Go files → `Task(subagent_type="go-engineer", ...)`
- Python files → `Task(subagent_type="python-engineer", ...)`

### Deep Mode: Specialized Sub-Agents

Invoke agents by their `subagent_type` (models defined in agent metadata):

**Go agents** (if Go files detected):

| subagent_type | Focus                        |
| ------------- | ---------------------------- |
| go-qa         | Logic, security, performance |
| go-tests      | Test coverage, quality       |
| go-impl       | Implementation concerns      |
| go-idioms     | Patterns, error handling     |
| go-docs       | Documentation, comments      |
| go-simplify   | Over-abstraction, dead code  |

**Python agents** (if Python files detected):

| subagent_type | Focus                        |
| ------------- | ---------------------------- |
| py-qa         | Logic, security, performance |
| py-tests      | Test coverage, quality       |
| py-impl       | Implementation concerns      |
| py-idioms     | Patterns, typing             |
| py-docs       | Docstrings, documentation    |
| py-simplify   | Over-abstraction, dead code  |

**TypeScript agents** (if TypeScript files detected):

| subagent_type | Focus                        |
| ------------- | ---------------------------- |
| ts-qa         | Logic, security, performance |
| ts-tests      | Test coverage, quality       |
| ts-impl       | Implementation concerns      |
| ts-idioms     | Patterns, strict typing      |
| ts-docs       | Documentation, comments      |
| ts-simplify   | Over-abstraction, dead code  |

**Web agents** (if HTML/CSS/JS files detected):

| subagent_type | Focus                           |
| ------------- | ------------------------------- |
| web-qa        | Security, performance, a11y     |
| web-tests     | E2E/Playwright test quality     |
| web-impl      | Requirements, responsiveness    |
| web-idioms    | Semantic HTML, CSS, JS patterns |
| web-docs      | Comments, ARIA labels           |
| web-simplify  | CSS bloat, unnecessary JS       |

Spawn each agent using its subagent_type directly:

```
Task(subagent_type="{agent}", prompt="Review code from: {git_command}. Output: file:line - Issue. Fix.")
```

Agent's own `model` setting (from metadata) is respected automatically.

### External Mode: Add Codex + Gemini (ONLY if `external` in arguments)

**Skip this section entirely if `external` is NOT in `$ARGUMENTS`.**

If `external` IS present, spawn these agents IN PARALLEL with Claude agents:

```
Task(subagent_type="codex-assistant", prompt="review: Review code from {git_command}")
Task(subagent_type="gemini-consultant", prompt="review: Review architecture of {git_command}")
```

**codex-assistant**: Code review for security (OWASP), quality, architecture, testing gaps.
**gemini-consultant**: Architecture alternatives and design trade-offs.

**Remember:** `deep` alone = Claude agents only. `deep external` = Claude + Codex + Gemini.

---

## Step 3: Aggregate & Present

```markdown
## Code Review Summary

**Mode**: {default|deep} {+external}
**Scope**: {description}
**Agents**: {count} reviewers

---

### CRITICAL (Must Fix)

- [{source}] `file:line` - Issue. Fix.

### IMPORTANT (Should Fix)

- [{source}] `file:line` - Issue. Fix.

### SUGGESTIONS

- [{source}] `file:line` - Issue. Fix.

---

### Consensus (Multi-Agent Agreement)

| Issue | Flagged By | Confidence |
| ----- | ---------- | ---------- |
| ...   | ...        | High       |

### Recommended Actions

1. {prioritized list}
```

---

## Examples

```
/reviewing-code                 # Claude only: go-engineer, python-engineer
/reviewing-code deep            # Claude only: 6-12 specialized sub-agents (NO external)
/reviewing-code external        # Claude engineers + Codex + Gemini
/reviewing-code deep external   # All Claude sub-agents + Codex + Gemini
```

**Execute this workflow now.**
