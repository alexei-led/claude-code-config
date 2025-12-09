---
allowed-tools: Task, Bash, AskUserQuestion, Read, Grep, Glob, mcp__codex__spawn_agent, mcp__gemini__ask-gemini
description: Multi-agent code review for security, quality, and architecture
---

# Multi-Agent Code Review

Review code like an experienced engineer using parallel AI agents.

## Step 1: Ask What to Review

Use AskUserQuestion with these options:

| Header       | Question                   | Options                                                                                                                                                                                                                            |
| ------------ | -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Review scope | What code should I review? | 1. **Uncommitted changes** - Review staged and unstaged changes (git diff HEAD) 2. **Branch vs master** - Review all commits on this branch (git diff master...HEAD) 3. **Specific files** - I'll provide file paths or paste code |

## Step 2: Get Code to Review

Based on user choice:

- **Uncommitted**: `git diff HEAD` (include `--staged` output too)
- **Branch vs master**: `git diff master...HEAD --stat` for overview, then full diff
- **Specific files**: Ask user for paths or accept pasted code

## Step 3: Detect Language & Generate Review Prompt

Detect primary language from file extensions (.go, .py, etc).

Generate an **Experienced Engineer Review Prompt**:

```
You are a senior {language} engineer conducting a thorough code review.

## Code Under Review
{diff or code content - keep concise, summarize if very large}

## Review Focus Areas

### Security (Critical)
- Input validation at boundaries
- SQL injection / command injection risks
- Authentication/authorization gaps
- Secrets or credentials exposure
- OWASP Top 10 vulnerabilities

### Code Quality
- {Go: error handling, interface design, goroutine safety}
- {Python: type hints, async patterns, PEP8 compliance}
- Readability and maintainability
- DRY violations and unnecessary complexity

### Architecture
- Clean architecture principles
- Dependency injection patterns
- Single responsibility adherence
- Appropriate abstraction levels

### Testing
- Test coverage for critical paths
- Edge case handling
- Mock usage appropriateness

## Output Format
Provide findings as:
1. **CRITICAL** - Must fix before merge (security, bugs)
2. **IMPORTANT** - Should fix (quality, patterns)
3. **SUGGESTION** - Nice to have (style, minor improvements)

Be specific: file:line, what's wrong, how to fix.
```

## Step 4: Spawn Parallel Reviewers

Launch ALL THREE reviewers in a SINGLE message (three parallel tool calls):

### Agent 1: Language Specialist (Task)

Language agents have their own tools - tell them what to review based on user's Step 1 choice:

- **Go code**: `Task` with `subagent_type=go-engineer`
- **Python code**: `Task` with `subagent_type=python-engineer`

```
"Review {scope description} for {language} best practices, bugs, and code quality.
{scope command - e.g., 'Run git diff HEAD' or 'Run git diff master...HEAD' or 'Read these files: ...'}
Focus on: error handling, interface design, concurrency safety, readability.
Format: CRITICAL/IMPORTANT/SUGGESTION with file:line references."
```

### Agent 2: Codex External Review (MCP)

Codex has its own tools - tell it what to review based on user's Step 1 choice:

```
mcp__codex__spawn_agent:
"Review {scope description} for bugs, security issues, and {language} best practices.
{scope command - e.g., 'Run git diff HEAD' or 'Run git diff master...HEAD' or 'Read these files: ...'}
Format: CRITICAL/IMPORTANT/SUGGESTION with file:line references."
```

### Agent 3: Gemini Architecture Review (MCP)

Gemini has its own tools - tell it what to review based on user's Step 1 choice:

```
mcp__gemini__ask-gemini:
"Review {scope description} for architecture and design issues.
{scope command - e.g., 'Run git diff HEAD' or 'Run git diff master...HEAD' or 'Read these files: ...'}
Focus on maintainability and patterns.
Format: severity + finding + recommendation with file:line references."
```

## Step 5: Aggregate & Present

Wait for all agents to complete, then consolidate:

```markdown
## Code Review Summary

### Critical Issues (Must Fix)

- [Source: Agent] Finding with file:line reference

### Important Issues (Should Fix)

- [Source: Agent] Finding with file:line reference

### Suggestions (Nice to Have)

- [Source: Agent] Finding with file:line reference

### Agreement Analysis

Issues flagged by multiple reviewers: [list]

### Recommended Actions

1. [Prioritized list of fixes]
```

## Context Optimization

- Keep code snippets under 2000 tokens per agent
- For large diffs, summarize and focus on changed logic
- Use `git diff --stat` first to identify key files
- Skip generated files, vendor directories, lock files

**Execute this workflow now.**
