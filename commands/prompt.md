---
allowed-tools: all
description: Synthesize a complete prompt by combining next.md with your arguments
---

## 🎯 PROMPT SYNTHESIZER

You will create a **complete, ready-to-copy prompt** by combining:
1. The next.md command template from ~/.claude/commands/next.md
2. The specific task details provided here: $ARGUMENTS

### 📋 YOUR TASK:

1. **READ** the next.md command file at ~/.claude/commands/next.md
2. **EXTRACT** the core prompt structure and requirements
3. **INTEGRATE** the user's arguments seamlessly into the prompt
4. **OUTPUT** a complete prompt in a code block that can be easily copied

### 🎨 OUTPUT FORMAT:

Present the synthesized prompt in a markdown code block like this:

```
[The complete synthesized prompt that combines next.md instructions with the user's specific task]
```

### ⚡ SYNTHESIS RULES:

1. **Preserve Structure** - Maintain the workflow, checkpoints, and requirements from next.md
2. **Integrate Naturally** - Replace `$ARGUMENTS` placeholder with the actual task details
3. **Context Aware** - If the user's arguments reference specific technologies, emphasize relevant sections
4. **Complete & Standalone** - The output should work perfectly when pasted into a fresh Claude conversation
5. **No Meta-Commentary** - Don't explain what you're doing, just output the synthesized prompt

### 🔧 ENHANCEMENT GUIDELINES:

- If the task mentions specific languages (Go, Python, etc.), emphasize those language-specific rules
- If the task seems complex, ensure the "ultrathink" and "multiple agents" sections are prominent
- If the task involves refactoring, highlight the "delete old code" requirements
- Keep ALL critical requirements (hooks, linting, testing) regardless of the task

### 📦 EXAMPLE BEHAVIOR:

If user provides: "implement a REST API for user management with JWT authentication"

You would:
1. Read next.md
2. Replace $ARGUMENTS with the user's task
3. Emphasize relevant sections (API design, security, testing)
4. Output the complete, integrated prompt

**BEGIN SYNTHESIS NOW** - Read next.md and create the perfect prompt!
