---
name: asking-codex
description: Code review, security audits, bug detection, alternative implementations, second opinions via OpenAI Codex. Use when user asks for code review, security analysis, implementation advice, bug detection, code patterns, or wants a second opinion on code. Supports uncommitted changes review. Do not use for architecture design or web searches.
allowed-tools: Task
---

# Codex Consultation

Spawn the **codex-assistant** agent for code-focused questions.

```
Task(subagent_type="codex-assistant", prompt="[mode]: <question>")
```

**Modes:** exec (default), review, plan, implement (add --auto for file changes)

The agent uses Codex MCP tools (`mcp__codex__codex`, `mcp__codex__review`) directly.
