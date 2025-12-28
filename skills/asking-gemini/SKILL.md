---
name: asking-gemini
description: Architecture advice via Gemini. Use for design trade-offs, brainstorming, comparing approaches.
allowed-tools: Task
---

# Gemini Consultation

Spawn the **gemini-consultant** agent for architecture and design questions.

```
Task(subagent_type="gemini-consultant", prompt="[mode]: <question>")
```

**Modes:** prompt, brainstorm, review, compare
