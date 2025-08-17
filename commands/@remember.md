---
allowed-tools: Task, mcp__basic-memory__write_note, mcp__basic-memory__read_note, mcp__basic-memory__search_notes, mcp__basic-memory__build_context, Read, LS, Grep
description: Save important project context and decisions using the orchestrator agent with basic-memory MCP
argument-hint: "[context or decision to remember]"
---

Use the orchestrator agent to save current project context, decisions, and patterns to basic-memory for future reference.

The orchestrator will:
- Analyze current project state and context
- Save architecture decisions and rationale
- Store coding patterns and conventions
- Document lessons learned and best practices
- Create searchable knowledge for future sessions

Perfect for:
- Saving important architecture decisions
- Documenting project patterns and conventions
- Preserving context across sessions
- Building organizational knowledge
- Creating searchable project memory

Example usage:
```
/remember "We decided to use PostgreSQL for user data with pgx driver and connection pooling"
```

This ensures important project knowledge is preserved and can be retrieved in future sessions.
