---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Read, Grep, LS
description: Group changes logically and create bundled commits with concise messages
---

Intelligently group changed files by logical relationship and create focused commits with descriptive messages.

**Commit Grouping Strategy:**
- Bundle related changes together (feature files, tests, docs)
- Separate concerns (config changes, code changes, documentation)
- Create atomic commits that make sense together

**Message Format:**
- Concise, present tense ("Add feature", "Fix bug", "Update docs")
- Focus on WHY, not just WHAT
- Include scope when relevant ("auth: add JWT validation")
- Never add Claude Code as (generated with and co-author)


**Workflow:**
1. Analyze all changed files and their relationships
2. Group into logical commits (feature + tests, config changes, docs)
3. Generate informative commit messages for each group
4. Execute commits in logical order

**Example Grouping:**
```
Group 1: Core feature implementation
- src/auth/jwt.go (new)
- src/auth/middleware.go (modified)
- internal/config/auth.go (modified)
Message: "auth: implement JWT token validation with middleware"

Group 2: Tests and validation
- src/auth/jwt_test.go (new)
- src/auth/middleware_test.go (modified)
Message: "auth: add comprehensive JWT validation tests"

Group 3: Documentation
- README.md (modified)
- docs/authentication.md (new)
Message: "docs: add JWT authentication documentation"
```

Use when you have multiple related changes that should be committed as focused, logical units rather than one large commit.
