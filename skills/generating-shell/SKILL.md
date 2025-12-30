---
name: generating-shell
description: Generates, explains, and plans shell commands, bash scripts, unix pipelines, awk/sed/grep expressions. Use when user requests shell commands, bash scripts, terminal commands, unix pipes, scripting help, or command syntax assistance. Do not use for web research or document analysis.
allowed-tools: Task
---

# Gemini Shell Helper

Spawn the **gemini-shell-helper** agent for shell command generation.

```
Task(subagent_type="gemini-shell-helper", prompt="<describe the shell task>")
```

Use for complex CLI pipelines, system administration tasks, or when you need help with command syntax.
