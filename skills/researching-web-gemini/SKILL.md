---
name: researching-web-gemini
description: Searches the web, researches topics online, finds current information using Gemini with Google Search grounding. Use when user asks to search the web, research information, find sources, look up current events, technology updates, or gather real-time data from the internet. Do not use for local file analysis or code execution.
allowed-tools: Task
---

# Gemini Web Research

Spawn the **gemini-researcher** agent for real-time web searches with Google grounding.

## When to Use This Skill (Gemini)

| Use Gemini For                 | Use Perplexity For                 |
| ------------------------------ | ---------------------------------- |
| Current events, breaking news  | Technology comparisons (X vs Y)    |
| Real-time data (<24 hours old) | Best practices, industry standards |
| Live pricing, availability     | OWASP, security guidelines         |
| Recent releases, changelogs    | Documentation references           |
| Rapidly changing information   | Stable technical content           |

**Use Gemini** when recency is critical (today's news, live data).
**Default to Perplexity** for most technical research.

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
