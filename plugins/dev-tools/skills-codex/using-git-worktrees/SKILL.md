---
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
description:
  Creates isolated git worktrees for parallel development. Use when starting
  feature work needing isolation or working on multiple branches simultaneously. Not
  for simple branch switching or basic git operations.
name: using-git-worktrees
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Git Worktrees

## Core Principle

**Main repo stays on main/master — never edit directly.** Every branch gets its own worktree (a sibling folder). Delete the worktree after the branch merges.

Think of a worktree as a **disposable branch folder**, not a long-lived parallel environment.

**Exception:** Trivial one-liner commits on a solo project can go directly on main to avoid ceremony overhead.

## Workflow

```bash
# 1. Create worktree for new work (from main repo)
git worktree add ../myproject-fix-cron -b fix-cron

# 2. Work there (open editor/Claude Code in that folder)
cd ../myproject-fix-cron

# 3. After PR is merged — clean up from main repo
cd ../myproject
git worktree remove ../myproject-fix-cron
git branch -d fix-cron
git pull
```

## Directory Layout

Worktrees are **sibling directories** (not nested inside the repo):

```
~/projects/
├── myproject/                    # main worktree — always on main, always clean
├── myproject-fix-cron/           # worktree for fix-cron branch
└── myproject-add-model/          # worktree for add-model branch
```

**Why siblings:** no .gitignore pollution, clean git status, independent build artifacts.

## Naming Convention

`<project>-<branch-slug>` — slashes become dashes, self-documenting.

| Branch             | Worktree Directory          |
| ------------------ | --------------------------- |
| `fix-cron`         | `../myproject-fix-cron`     |
| `feature/auth`     | `../myproject-feature-auth` |
| `bugfix/issue-123` | `../myproject-bugfix-123`   |

## When to Suggest Worktrees

- User wants to start a new feature, fix, or experiment
- User is about to edit code on main/master
- User wants to try multiple approaches to the same problem
- User has uncommitted changes and wants to start something else

## References

- [WORKFLOW.md](WORKFLOW.md) - Detailed steps, project setup, common mistakes
- [scripts/](scripts/) - Helper script for automated setup
