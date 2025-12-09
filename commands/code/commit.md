---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*), Read, Grep, LS
description: Group changes logically and create bundled commits with concise messages
---

# Smart Commit

Group changed files logically and create focused, atomic commits.

## Step 1: Analyze Changes

```bash
git status
git diff --stat HEAD
```

## Step 2: Group by Logical Relationship

| Group Type   | Files to Bundle                         |
| ------------ | --------------------------------------- |
| Feature      | Implementation + related config + tests |
| Refactor     | All files touched by the refactor       |
| Fix          | Bug fix + test that verifies it         |
| Docs         | Documentation changes only              |
| Config/Infra | Build, CI, deployment changes           |

## Step 3: Commit Each Group

For each group:

```bash
git add <files in group>
git commit -m "<scope>: <action> <what>

<optional body explaining WHY>"
```

**Message Format:**

- Present tense: "Add", "Fix", "Update", "Remove"
- Scope prefix when relevant: `auth:`, `api:`, `docs:`
- Focus on WHY, not just WHAT
- Never mention Claude Code or AI generation

## Example

```
Group 1: Core feature
- src/auth/jwt.go (new)
- src/auth/middleware.go (modified)
→ git commit -m "auth: implement JWT validation with middleware"

Group 2: Tests
- src/auth/jwt_test.go (new)
→ git commit -m "auth: add JWT validation tests"

Group 3: Documentation
- README.md (modified)
→ git commit -m "docs: add JWT authentication guide"
```

## Single Change?

If only one logical change exists, create one commit. Don't force grouping.

**Execute commit workflow now.**
