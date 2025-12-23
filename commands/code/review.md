---
allowed-tools: Task, AskUserQuestion, Bash
description: Multi-agent code review for security, quality, and architecture
argument-hint: [deep] [external]
---

# Multi-Agent Code Review

**Parse `$ARGUMENTS`:**

- `deep` → 6-12 specialized sub-agents instead of language engineers
- `external` → Add Codex + Gemini reviewers

| Arguments     | Local Agents                                                        | External       |
| ------------- | ------------------------------------------------------------------- | -------------- |
| (none)        | go-engineer, python-engineer                                        | No             |
| deep          | go-qa, go-idioms, go-tests, go-impl, go-docs, go-simplify (+ py-\*) | No             |
| external      | go-engineer, python-engineer                                        | Codex + Gemini |
| deep external | All 6-12 sub-agents                                                 | Codex + Gemini |

---

## Step 1: Detect Language & Ask Scope

Detect languages in changes:

```bash
git diff --name-only HEAD | grep -E '\.(go|py|ts|tsx)$' | head -20
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

Spawn each agent using its subagent_type directly:

```
Task(subagent_type="{agent}", prompt="Review code from: {git_command}. Output: file:line - Issue. Fix.")
```

Agent's own `model` setting (from metadata) is respected automatically.

### External Mode: Add Codex + Gemini

If `external` in arguments, ALSO use the **asking-codex** and **asking-gemini** skills for additional review perspectives:

**Codex** (via asking-codex skill): Delegate code review for a senior engineer perspective on security (OWASP), code quality, architecture, and testing gaps.

**Gemini** (via asking-gemini skill): Consult Gemini AI for architecture alternatives and design trade-offs on the code changes.

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
/code:review                    # Go/Python engineers only
/code:review deep               # 6-12 specialized sub-agents
/code:review external           # Engineers + Codex + Gemini
/code:review deep external      # All sub-agents + Codex + Gemini
```

**Execute this workflow now.**
