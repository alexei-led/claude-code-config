---
allowed-tools:
  - Bash(gemini *)
  - Read
  - Grep
  - Glob
argument-hint: "[question or topic]"
description:
  Consult Gemini for second opinions, brainstorming, or web search. Use
  when user says "ask gemini", "gemini search", "get gemini opinion", or wants a second
  AI perspective.
name: using-gemini
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Gemini CLI Integration

Consult Google Gemini via CLI for second opinions, brainstorming, or web search.

## Usage

Run Gemini in non-interactive (headless) mode:

```bash
# General query
gemini -p "your question here"

# With specific model
gemini -m gemini-2.5-pro -p "your question"

# Pipe context into Gemini
cat file.go | gemini -p "review this code for issues"
```

## When to Use

- **Second opinion**: Get Gemini's perspective on architecture, design, or code
- **Web search**: Ask Gemini to search for current information
- **Brainstorming**: Generate alternative approaches or ideas
- **Media analysis**: Describe images or analyze file content

## Workflow

1. Gather relevant context from the codebase if needed
2. Formulate a clear prompt
3. Run `gemini -p "prompt"` for non-interactive response
4. Summarize findings back to the user

## Tips

- Keep prompts focused and specific for best results
- Pipe file content directly when asking about specific code
- Use `-m` flag to select a specific Gemini model if needed
