---
description: Audit AI coding-agent configuration against current features and local
  usage. Use when the user wants to improve Claude Code, Pi, Codex, Gemini, skill,
  hook, or agent configuration.
name: evolving-config
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# Evolving Agent Configuration in Pi

Audit config with local evidence first, then current docs or web evidence when
needed. Do not rewrite config because a blog post looked shiny. That way lies
confetti architecture.

## Scope

Review:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`
- `.claude/`, `.pi/`, `.codex/`, `.agents/`
- plugin skills, agents, hooks, commands, and generated exports
- chezmoi-managed copies when deployment is part of the request

## Workflow

1. Identify the config surface and the user's goal.
2. Read current files before suggesting changes.
3. Check generated-file rules before editing generated outputs.
4. Use `context7-cli` for library or tool docs when syntax is uncertain.
5. Use `web_search` or `web_answer` for current public docs, release notes, or
   feature availability.
6. Prefer small, reversible changes. Ask before deleting or moving private
   config.
7. Verify with the repo's validation commands.

## Findings To Prioritize

- unsupported tool names
- stale generated docs or overlays
- duplicate skills or agents
- broad trigger descriptions that cause accidental activation
- hooks that can block safe work or hide errors
- secrets or private data in prompt/config files
- generated files edited by hand

## Output Contract

```markdown
## Config Audit

### Critical
- `path:line` — issue. Fix: action.

### Important
- `path:line` — issue. Fix: action.

### Suggested
- `path:line` — issue. Fix: action.

### Verification
- command to run
```
