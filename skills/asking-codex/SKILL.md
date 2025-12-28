---
name: asking-codex
description: Code review via Codex. Use for security audits, bug detection, alternative implementations, second opinions.
allowed-tools: Task
---

# Codex Consultation

Spawn the **codex-assistant** agent for code-focused questions.

```
Task(subagent_type="codex-assistant", prompt="[mode]: <question>")
```

**Modes:** exec, review, plan, implement (add --auto for file changes)
