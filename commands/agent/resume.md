---
allowed-tools:
  - Task
  - TaskOutput
description: Resume a previously spawned agent by ID
argument-hint: <agent_id>
---

# Resume Agent

Continue work with a previously spawned agent using its ID.

**Usage**: `/agent:resume <agent_id>`

## Examples

```
/agent:resume a3c6662
/agent:resume abc123 with "continue investigating the auth flow"
```

## How to Find Agent IDs

Agent IDs are returned when you spawn background agents:

```
Task(subagent_type="go-engineer", run_in_background=true, ...)
→ Returns: agentId: a3c6662
```

## Execution

Parse `$ARGUMENTS`:

- First word = agent ID
- Remaining = additional context/prompt (optional)

**Resume the agent:**

```
Task(resume="<agent_id>", prompt="<additional context if provided>")
```

If no additional prompt provided, the agent continues from where it left off.

**Execute resume now.**
