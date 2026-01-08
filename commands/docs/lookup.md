---
allowed-tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
description: Look up library documentation via Context7
argument-hint: <library> [topic]
---

# Documentation Lookup

Fetch up-to-date library documentation via Context7 for: **$ARGUMENTS**

Use the **looking-up-docs** skill to find API references, code examples, and usage patterns.

Parse arguments: first word = library, remaining = topic.

## Output Format

- Key APIs and signatures
- Code examples
- Usage patterns

If insufficient, try `mode="info"` or `page=2,3`.

**Execute lookup now using the looking-up-docs skill.**
