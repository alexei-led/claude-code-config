# dev-tools

Developer utilities: modern CLI tools, git worktrees, docs lookup, web research,
brainstorming, config review, and local history. Skills are exported for Claude
Code, Codex CLI, Gemini CLI, and Pi; agents and hooks are Claude Code-only unless
ported under `platforms/pi/agents`.

## Skills (17)

| Skill                  | Invocable | What It Does                                  |
| ---------------------- | --------- | --------------------------------------------- |
| `brainstorming-ideas`  | yes       | Brainstorm ideas and stress-test draft plans  |
| `grill-me`             | yes       | Relentless decision-tree interview on one plan |
| `debating-ideas`       | yes       | Dialectic agents stress-test design decisions |
| `context7-cli`         | yes       | Current library docs through the `ctx7` CLI   |
| `looking-up-docs`      | yes       | Compatibility router to `context7-cli`        |
| `researching-web`      | yes       | Web research via available web providers      |
| `analyzing-usage`      | yes       | Analyze Claude Code usage, cost, and efficiency |
| `evolving-config`      | yes       | Audit coding-agent config and generated exports |
| `using-gemini`         | yes       | Consult Gemini CLI for second opinions        |
| `learning-patterns`    | auto      | Extract learnings and generate customizations |
| `linting-instructions` | yes       | Lint skill and agent instruction quality      |
| `reviewing-cc-config`  | yes       | Review Claude Code config for context efficiency |
| `exploring-repos`      | yes       | Explore public GitHub repos and architecture  |
| `smart-explore`        | auto      | Token-efficient local code navigation         |
| `mem-history`          | yes       | Query project history and prior decisions     |
| `using-git-worktrees`  | auto      | Isolated git worktree management              |
| `using-modern-cli`     | auto      | rg, fd, bat, eza, sd instead of legacy tools  |

## Agents (2, Claude Code)

- `perplexity-researcher` (sonnet) — codebase-aware web research
- `pdf-parser` (sonnet) — PDF parsing and structured data extraction

## Hooks (2, Claude Code)

| Hook                 | Event          | What It Does                  |
| -------------------- | -------------- | ----------------------------- |
| `worktree-create.sh` | WorktreeCreate | Sets up isolated git worktree |
| `worktree-remove.sh` | WorktreeRemove | Cleans up worktree on exit    |

## External Providers

| Provider | Used For |
| --- | --- |
| Context7 CLI (`ctx7`) | Portable library documentation lookup |
| Perplexity/web providers | Research and current facts when available |
| Gemini CLI | Second opinions and search when explicitly requested |

Claude Code-only source agents may use optional MCP providers. Pi exports do not
assume MCP tools.
