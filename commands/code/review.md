---
context: fork
allowed-tools:
  - Task
  - TodoWrite
  - AskUserQuestion
  - Bash
description: Multi-agent code review for security, quality, and architecture
argument-hint: [deep]
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

| Arguments | Claude Agents                                                                      |
| --------- | ---------------------------------------------------------------------------------- |
| (none)    | go-engineer, python-engineer, typescript-engineer, web-engineer                    |
| deep      | go-qa, go-idioms, go-tests, go-impl, go-docs, go-simplify (+ py-\*, ts-\*, web-\*) |

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
- TypeScript files → `Task(subagent_type="typescript-engineer", ...)`
- Web files (HTML/CSS/JS) → `Task(subagent_type="web-engineer", ...)`

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

---

## Step 3: Aggregate & Present

```markdown
## Code Review Summary

**Mode**: {default|deep}
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
/code:review                    # Claude only: go-engineer, python-engineer
/code:review deep               # Claude only: 6-12 specialized sub-agents
```

**Execute this workflow now.**
