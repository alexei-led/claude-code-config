---
allowed-tools:
  - Task
  - Read
  - Bash(jq:*)
description: Quick progress check for spec-driven development
---

# Spec Status

Quick snapshot of spec-driven development progress.

**Spawn `spec-discover` agent:**

```
Task(subagent_type="spec-discover", prompt="Quick status check - return discovery summary")
```

Display the agent's report directly to user.
