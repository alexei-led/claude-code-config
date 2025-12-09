---
allowed-tools: Task, Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*)
description: Group changes logically and create bundled commits with concise messages
---

# Smart Commit

Group changed files logically and create focused, atomic commits.

## Step 1: Analyze Changes with Sub-Agent

Spawn an **Explore** agent (subagent_type: Explore) to analyze and group changes:

```
Analyze git changes and propose commit groupings:

1. Run `git status` to see all changed files
2. Run `git diff --stat HEAD` for change overview
3. Run `git log --oneline -5` for recent commit style reference
4. Read key changed files to understand the nature of changes

Group files by logical relationship:
| Group Type   | Files to Bundle                         |
| Feature      | Implementation + related config + tests |
| Refactor     | All files touched by the refactor       |
| Fix          | Bug fix + test that verifies it         |
| Docs         | Documentation changes only              |
| Config/Infra | Build, CI, deployment changes           |

For each group, draft a commit message:
- Present tense: "Add", "Fix", "Update", "Remove"
- Scope prefix when relevant: `auth:`, `api:`, `docs:`
- Focus on WHY, not just WHAT
- Match style of recent commits

Return structured proposal:
GROUP 1: [type]
Files: [list]
Message: "<scope>: <action> <what>"

GROUP 2: [type]
...

If only one logical change exists, propose a single commit.
```

## Step 2: Review and Execute

Review the agent's grouping proposal, then for each group:

```bash
git add <files in group>
git commit -m "<proposed message>"
```

Verify after committing:

```bash
git status
```

**Execute commit workflow now.**
