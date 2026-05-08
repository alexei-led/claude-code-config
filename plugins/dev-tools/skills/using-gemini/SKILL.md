---
name: using-gemini
description: Consult Gemini for second opinions, brainstorming, or web search. Use when user says "ask gemini", "gemini search", "get gemini opinion", or wants a second AI perspective.
user-invocable: true
disable-model-invocation: true
context: fork
allowed-tools:
  - Bash(gemini *)
  - Read
  - Grep
  - Glob
argument-hint: "[question or topic]"
---

# Gemini CLI Integration

Consult Google Gemini via CLI for second opinions, brainstorming, or web search.

## Critical Workflow Rules

- When the user asks to "ask Gemini" or "gemini search", run the `gemini` CLI when available; do not only suggest a command.
- Scope what is sent. Do not send secrets, credentials, private code, or whole repos unless the user explicitly approves and the context is necessary.
- For second opinions, compare Gemini output against local code, requirements, ADRs, or other existing evidence. Gemini is critique, not authority.
- For web/search use, ask Gemini for recent examples with source URLs, then cross-check against official docs or local project constraints before recommending changes.
- Final synthesis must separate: agreements, disagreements, unsupported claims, and actionable next steps.
- If Gemini is unavailable, report the exact blocker and provide the command that would be run.

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

1. Gather only the relevant context from the codebase if needed
2. Formulate a clear, scoped prompt
3. Run `gemini -p "prompt"` for non-interactive response
4. Verify or cross-check Gemini's claims against local evidence or official sources
5. Summarize agreements, disagreements, unsupported claims, and actionable next steps

## Tips

- Keep prompts focused and specific for best results
- Pipe file content directly when asking about specific code
- Use `-m` flag to select a specific Gemini model if needed
