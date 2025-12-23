---
name: researching-web
description: |
  Searches the web via Perplexity AI for current information. Use when needing best practices, technology comparisons, or factual questions about tools. Not for library documentation (use looking-up-docs instead).

  <example>
  user: "What are Go error handling best practices in 2025?"
  → Use this skill for current best practices
  </example>

  <example>
  user: "Compare Redis vs Memcached for session storage"
  → Use this skill for technology comparisons
  </example>
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
