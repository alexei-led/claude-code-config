---
name: researching-web
description: Web research via Perplexity. Use for best practices, technology comparisons, current information.
allowed-tools: Read, Grep, Glob, mcp__perplexity-ask__perplexity_ask
---

# Web Research with Perplexity

Use `mcp__perplexity-ask__perplexity_ask` for web search.

## When to Use

- Best practices and recommendations
- Current information (releases, news)
- Comparisons between technologies
- Factual questions about tools/libraries

## Usage

```json
{
  "messages": [{ "role": "user", "content": "Your research question" }]
}
```

## Tips

- Be specific: "Go error handling best practices 2024"
- Include context: "Redis vs Memcached for session storage"
- Ask comparisons: "Pros and cons of gRPC vs REST"
