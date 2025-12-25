---
name: asking-codex
description: |
  Delegates coding tasks to OpenAI Codex agent. Use for code review (/review), implementation help, or autonomous task execution. Not for research or documentation.

  <example>
  user: "Get a second opinion on this algorithm"
  → Use this skill for alternative implementation perspectives
  </example>

  <example>
  user: "Have Codex review my code changes"
  → Use this skill for external code review
  </example>
allowed-tools: Bash
---

# Code Tasks with Codex CLI

Invoke Codex CLI for code review, implementation, and autonomous coding tasks.

## Sandbox Requirement

**IMPORTANT**: Codex CLI requires sandbox disabled due to macOS SystemConfiguration API usage.
When invoking Bash for codex commands, you MUST use: `dangerouslyDisableSandbox: true`

## Quick Usage

```bash
# Non-interactive exec
codex exec "Your task description"

# With file modifications
codex exec --full-auto "Add validation to form"

# With helper script
~/.claude/skills/asking-codex/scripts/ask.sh review "Check for security issues"
~/.claude/skills/asking-codex/scripts/ask.sh plan "Implement user auth"
~/.claude/skills/asking-codex/scripts/ask.sh implement --auto "Add error handling"
```

## When to Use

| Use Case       | Example                                   |
| -------------- | ----------------------------------------- |
| Code review    | "Review recent changes for issues"        |
| Second opinion | "Alternative approach for this algorithm" |
| Implementation | "Add input validation" (with --auto)      |
| Task planning  | "Break down auth feature into steps"      |

## Modes

The helper script supports context-aware modes:

| Mode        | Purpose                                 |
| ----------- | --------------------------------------- |
| `exec`      | Raw exec (default)                      |
| `review`    | Code review with line-specific feedback |
| `plan`      | Break task into implementation steps    |
| `implement` | Implement following existing patterns   |

Add `--auto` for file modifications.

## References

- [COMMANDS.md](COMMANDS.md) - Slash commands and exec flags
- [scripts/ask.sh](scripts/ask.sh) - Helper script
