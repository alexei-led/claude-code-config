---
name: second-opinion
description: Consult alternative AI models for code review or design decisions. Use Codex for implementation review and code quality feedback. Use Gemini for architecture alternatives and design trade-offs. Invoke when seeking validation or alternative perspectives.
---

# Second Opinion Consultation

## When to Use

| Model      | Use For                                                              |
| ---------- | -------------------------------------------------------------------- |
| **Codex**  | Code review, implementation quality, bug detection                   |
| **Gemini** | Architecture alternatives, design trade-offs, different perspectives |

## Codex (Code Review)

Use `mcp__codex__spawn_agent` for:

- Review code quality and patterns
- Find potential bugs or edge cases
- Suggest improvements to implementation
- Validate approach against best practices

**Prompt pattern**: "Review this code for [quality/bugs/patterns]: [code or file reference]"

## Gemini (Design Consultation)

Use Gemini MCP tools for:

- Alternative architecture approaches
- Trade-off analysis between options
- Challenge assumptions
- Different perspective on design decisions

**Prompt pattern**: "I'm considering [approach]. What are alternatives and trade-offs?"

## Workflow

1. Form your initial solution/design
2. Choose: implementation question → Codex, design question → Gemini
3. Compare feedback with your approach
4. Synthesize best ideas from both perspectives
