---
name: using-git-worktrees
description: Creates isolated git worktrees for parallel development. Use when starting feature work needing isolation or working on multiple branches simultaneously. Not for simple branch switching or basic git operations.
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Git Worktrees

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously.

## Quick Start

```bash
# Create worktree as sibling directory (best practice)
git worktree add ../myproject-feature-auth -b feature/auth

# Create from existing branch
git worktree add ../myproject-bugfix-123 bugfix/issue-123

# List all worktrees
git worktree list

# Remove when done
git worktree remove ../myproject-feature-auth

# Clean up stale entries
git worktree prune
```

## Directory Strategy

Worktrees are created as **sibling directories** to the main repo (not inside it):

```
~/projects/
├── myproject/                    # main worktree (main branch)
├── myproject-feature-auth/       # linked worktree
└── myproject-hotfix-login/       # linked worktree
```

**Why siblings, not children:**

- No .gitignore pollution — worktree is outside the repo
- Cleaner `git status` — no risk of tracking worktree contents
- Standard practice endorsed by git docs and community
- Each worktree has independent build artifacts, node_modules, etc.

## Naming Convention

`<project>-<branch-slug>` — self-documenting, instantly shows purpose.

| Branch             | Worktree Directory           |
| ------------------ | ---------------------------- |
| `feature/auth`     | `../myproject-feature-auth`  |
| `bugfix/issue-123` | `../myproject-bugfix-123`    |
| `experiment/v2`    | `../myproject-experiment-v2` |

## References

- [WORKFLOW.md](WORKFLOW.md) - Detailed workflow steps
- [scripts/](scripts/) - Helper scripts
