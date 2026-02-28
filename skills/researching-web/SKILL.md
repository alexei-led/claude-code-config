---
name: researching-web
description: Web research via Perplexity AI. Use for technical comparisons (X vs Y), best practices, industry standards, documentation. Triggers on "research", "compare", "vs", "best practice", "which is better", "pros and cons".
context: fork
allowed-tools:
  - Task
  - Read
  - Grep
  - Glob
  - WebFetch
  - mcp__perplexity-ask__perplexity_ask
---

# Web Research with Perplexity

**Default**: Call Perplexity MCP directly. Only spawn agent when codebase context is explicitly needed.

## Best For

- Technology comparisons (X vs Y)
- Best practices, industry standards
- OWASP, security guidelines
- Documentation references
- Stable technical content

## Default Mode: Direct MCP Call

**Use this for 90% of research requests.** When user says "ask Perplexity", "research", "look up", etc.:

```json
mcp__perplexity-ask__perplexity_ask({
  "messages": [{ "role": "user", "content": "Your research question" }]
})
```

This is fast, reliable, and what users expect.

## Deep Mode: Agent (Rare)

**Only use when user explicitly asks to compare research with their current code.**

Trigger phrases that warrant agent:

- "compare my code to best practices"
- "is my implementation following standards"
- "research and show how my code differs"

```
Task(subagent_type="perplexity-researcher", prompt="Research: <topic>", run_in_background=true)
```

**DO NOT use agent for:**

- Simple "ask Perplexity about X" requests
- General research questions
- "What is the best way to do X" (unless they mention their code)

## Query Formulation Tips

- Be specific: "Go 1.25 error handling best practices 2025"
- Include context: "Redis vs Memcached for session storage in Go services"
- Ask comparisons: "Pros and cons of gRPC vs REST for microservices"
- Include year: "Claude Code context optimization 2025"

## Reference Following (Deep Research)

After Perplexity returns results with citations:

1. **Review all cited URLs** in the response
2. **WebFetch top 2-3 most relevant sources** for deeper context
3. **Synthesize comprehensive answer** combining all sources

```
# After Perplexity response with citations
WebFetch(url="<cited-url-1>", prompt="Extract key details about <topic>")
WebFetch(url="<cited-url-2>", prompt="Extract implementation examples")
```

Use reference following when:

- Initial answer is high-level and needs specifics
- User asks "tell me more" or "dig deeper"
- Implementing something that needs detailed guidance

## Output Structure

```markdown
## Summary

[Key findings - 2-3 sentences]

## Details

[Organized findings by topic]

## Recommendations

[Actionable items for the project]

## Sources

- [Source](url) - [what was learned]
```
