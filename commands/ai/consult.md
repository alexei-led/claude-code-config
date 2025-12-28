---
allowed-tools: Task, AskUserQuestion
description: Consult AI assistants for code review, architecture, or brainstorming
argument-hint: [codex|gemini|panel|brainstorm|review|compare] <question>
---

# AI Consultation

Consult external AI assistants for specialized input.

**Parse `$ARGUMENTS` for mode:**

- `codex` or `review` → Code review, security, bugs (codex-assistant)
- `gemini` or `design` or `brainstorm` or `compare` → Architecture, trade-offs (gemini-consultant)
- `panel` → Multi-perspective from all AIs (ai-panel)
- (no mode) → Ask user which AI to consult

**If no mode specified, ask:**

```
AskUserQuestion:
  question: "Which AI assistant should I consult?"
  header: "AI Source"
  options:
    - label: "Codex (code review)"
      description: "Security audits, bug detection, implementation review"
    - label: "Gemini (architecture)"
      description: "Design trade-offs, brainstorming, comparing approaches"
    - label: "Panel (all AIs)"
      description: "Multi-perspective from Codex, Gemini, Claude, Perplexity"
```

**Spawn appropriate agent:**

- Codex → `Task(subagent_type="codex-assistant", prompt="review: $ARGUMENTS")`
- Gemini → `Task(subagent_type="gemini-consultant", prompt="$ARGUMENTS")`
- Panel → `Task(subagent_type="ai-panel", prompt="Consult panel on: $ARGUMENTS")`

Present the agent's summary to the user.

**Execute consultation now.**
