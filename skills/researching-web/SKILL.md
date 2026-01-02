---
name: researching-web
description: Web research via Perplexity AI. Use when user asks to research topics, compare technologies (X vs Y), find best practices, lookup industry standards, or get current information. Triggers on "research", "compare", "vs", "best practice", "pros and cons", "which is better".
allowed-tools: Task, Read, Grep, Glob, mcp__perplexity-ask__perplexity_ask
---

# Web Research with Perplexity

Two modes: **quick** (MCP direct) or **deep** (Task-based with context).

## When to Use This Skill (Perplexity)

| Use Perplexity For                 | Use Gemini For                 |
| ---------------------------------- | ------------------------------ |
| Technology comparisons (X vs Y)    | Current events, breaking news  |
| Best practices, industry standards | Real-time data (<24 hours old) |
| OWASP, security guidelines         | Live pricing, availability     |
| Documentation references           | Recent releases, changelogs    |
| Stable technical content           | Rapidly changing information   |

**Default to Perplexity** for most technical research.
**Use Gemini** when recency is critical (today's news, live data).

## Quick Mode (Simple Queries)

Use MCP directly for fast, simple lookups:

```json
mcp__perplexity-ask__perplexity_ask({
  "messages": [{ "role": "user", "content": "Your research question" }]
})
```

## Deep Mode (Context-Aware Research)

For codebase-aware research, spawn the **perplexity-researcher** agent.

### Foreground (blocking)

```
Task(subagent_type="perplexity-researcher", prompt="Research: <topic>")
```

### Background (recommended for context efficiency)

Run in background to avoid polluting main context:

```
Task(
  subagent_type="perplexity-researcher",
  prompt="Research: <topic>",
  run_in_background=true
)
```

Retrieve results when ready:

```
TaskOutput(task_id="<agent_id>", block=true)
```

**Use background mode when:**

- Running multiple research queries in parallel
- Main task can continue while research runs
- Want to keep main context clean

### When to Use Deep Mode

- User asks "best way to do X" (needs to compare with current code)
- Researching improvements to existing code
- Need to understand if recommendations apply to current stack

## Query Formulation Tips

- Be specific: "Go 1.25 error handling best practices 2025"
- Include context: "Redis vs Memcached for session storage in Go services"
- Ask comparisons: "Pros and cons of gRPC vs REST for microservices"
- Include year: "Claude Code context optimization 2025"

## Output Structure

```markdown
## Summary

[Key findings - 2-3 sentences]

## Details

[Organized findings by topic]

## Recommendations

[Actionable items for the project]

## Sources

- [Source](url)
```
