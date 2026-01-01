---
name: researching-web-gemini
description: Searches the web, researches topics online, finds current information using Gemini with Google Search grounding. Use when user asks to search the web, research information, find sources, look up current events, technology updates, or gather real-time data from the internet. Do not use for local file analysis or code execution.
allowed-tools: Task
---

# Gemini Web Research

Spawn the **gemini-researcher** agent for real-time web searches with Google grounding.

## Foreground (blocking)

```
Task(subagent_type="gemini-researcher", prompt="<search query>")
```

## Background (for context efficiency)

```
Task(subagent_type="gemini-researcher", prompt="<query>", run_in_background=true)
```

Use `TaskOutput(task_id="<id>")` to retrieve results.

Use when you need current, up-to-date information that may not be in Claude's training data.
