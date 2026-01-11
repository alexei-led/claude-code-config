---
context: fork
model: sonnet
allowed-tools:
  - Task
description: Get independent code/design review from fresh Claude perspective
argument-hint: <question or file to review>
---

# AI Consultation

Get independent review from a fresh Claude perspective (no prior context).

**Spawn claude-reviewer agent:**

```
Task(
  subagent_type="claude-reviewer",
  prompt="Review: $ARGUMENTS

Provide independent analysis with fresh perspective.
Focus on: correctness, design, potential issues, improvements."
)
```

Present the agent's findings to the user.

**Execute consultation now.**
