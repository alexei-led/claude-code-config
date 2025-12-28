---
allowed-tools: Task
description: Consult Codex for code review or implementation advice
argument-hint: [review|plan] <topic>
---

# Codex Consultation

Consult OpenAI Codex for code-focused perspectives.

**Parse `$ARGUMENTS`:**

- `review` → Code review mode
- `plan` → Implementation planning mode
- (default) → General code consultation

Spawn the **codex-assistant** agent:

```
Task(subagent_type="codex-assistant", prompt="[MODE]: $ARGUMENTS")
```

Present the agent's summary to the user.

**Execute consultation now.**
