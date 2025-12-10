---
allowed-tools: Task, AskUserQuestion, mcp__codex__spawn_agent, mcp__gemini__ask-gemini
description: Multi-agent code review for security, quality, and architecture
---

# Multi-Agent Code Review

Review code using three parallel AI agents. Main context stays clean for synthesis.

## Step 1: Ask What to Review

Use AskUserQuestion with these options:

| Header       | Question                   | Options                                                                                                                                                                                                                            |
| ------------ | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Review scope | What code should I review? | 1. **Uncommitted changes** - Review staged and unstaged changes (git diff HEAD) 2. **Branch vs master** - Review all commits on this branch (git diff master...HEAD) 3. **Specific files** - I'll provide file paths or paste code |

## Step 2: Detect Language & Build Review Prompt

Based on user's scope choice, detect primary language from mentioned file extensions or ask if unclear.

**Generate this review prompt** (fill in {placeholders}):

```
You are a senior {language} engineer conducting a thorough code review.

## Your Task

1. First, run the appropriate git command to get the code:
   {git_command_recommendation}

2. Review the output focusing on the areas below.

## Review Focus Areas

### Security (Critical)
- Input validation at boundaries
- SQL injection / command injection risks
- Authentication/authorization gaps
- Secrets or credentials exposure
- OWASP Top 10 vulnerabilities

### Code Quality ({language}-specific)
- {Go: error handling, interface design, goroutine safety, defer patterns}
- {Python: type hints, async patterns, exception handling, PEP8}
- Readability and maintainability
- DRY violations and unnecessary complexity

### Architecture
- Clean architecture principles
- Dependency injection patterns
- Single responsibility adherence
- Appropriate abstraction levels

### Testing Considerations
- Missing test coverage for critical paths
- Edge cases that need handling
- Potential mock/stub needs

## Output Format

Provide findings ONLY in this format:

### CRITICAL (Must Fix)
- `file:line` - Issue description. Recommendation.

### IMPORTANT (Should Fix)
- `file:line` - Issue description. Recommendation.

### SUGGESTIONS (Nice to Have)
- `file:line` - Issue description. Recommendation.

Be specific with file:line references. Skip praise - only actionable findings.
```

**Git command recommendations by scope:**

- Uncommitted changes: `git diff HEAD` (also check `git diff --staged`)
- Branch vs master: `git diff master...HEAD`
- Specific files: `cat {file_paths}` or read the provided code directly

## Step 3: Spawn All Three Reviewers in Parallel

Launch ALL THREE in a SINGLE message with the SAME generated prompt:

### Agent 1: Language Specialist (Task)

Use `Task` tool with appropriate `subagent_type`:

- Go code → `subagent_type=go-engineer`
- Python code → `subagent_type=python-engineer`

Pass the generated review prompt.

### Agent 2: Codex (MCP)

Use `mcp__codex__spawn_agent` with the same generated review prompt.

### Agent 3: Gemini (MCP)

Use `mcp__gemini__ask-gemini` with the same generated review prompt.

## Step 4: Aggregate & Present

Wait for all agents to complete, then consolidate findings:

```markdown
## Code Review Summary

### Critical Issues (Must Fix)

- [Source: Agent] Finding with file:line reference

### Important Issues (Should Fix)

- [Source: Agent] Finding with file:line reference

### Suggestions (Nice to Have)

- [Source: Agent] Finding with file:line reference

### Consensus Analysis

Issues flagged by multiple reviewers (higher confidence):

- [list overlapping findings]

### Recommended Actions

1. [Prioritized fix list]
```

## Key Principles

- **Agents do the git work** - Main context stays clean
- **Same prompt to all** - Consistent review scope
- **Parallel execution** - All three agents in one message
- **You synthesize** - Aggregate, dedupe, prioritize findings

**Execute this workflow now.**
