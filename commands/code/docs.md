---
allowed-tools: Task, AskUserQuestion, Read, Write, Edit, Grep, Glob, LS, mcp__context7__resolve-library-id, mcp__context7__get-library-docs
description: Update all documentation based on recent changes using docs-keeper agent
---

# Documentation Update

Update project documentation to reflect current code state.

## Step 1: Ask What to Document

Use AskUserQuestion:

| Header    | Question                            | Options                                                                                                                                                                                                        |
| --------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Doc scope | What documentation should I update? | 1. **Auto-detect** - Scan for outdated docs based on recent changes 2. **README** - Update project README 3. **API docs** - Update API/function documentation 4. **All** - Comprehensive documentation refresh |

## Step 2: Analyze Current State

Based on user choice:

### Auto-detect

```bash
# Find recently changed code
git diff --name-only HEAD~5 | grep -E "\.(go|py)$"

# Find existing docs
find . -name "*.md" -o -name "doc.go" | head -20
```

Compare code changes with doc timestamps.

### README Focus

Read current README.md and compare with:

- Project structure (`ls -la`)
- Available make targets (`make help` or parse Makefile)
- Dependencies (go.mod, requirements.txt, package.json)

### API Docs Focus

- **Go**: Scan for missing/outdated GoDoc comments on exported functions
- **Python**: Check docstrings on public functions/classes

## Step 3: Spawn docs-keeper Agent

```
Task with docs-keeper agent:
"Update documentation for this project:

Scope: {user's choice}
Recent changes: {list of changed files}

Focus on:
- Accurate function/method documentation
- Updated README sections
- Architecture diagram if significant changes
- API endpoint documentation

Use Context7 to research documentation best practices if needed."
```

## Step 4: Verify Updates

After agent completes:

- Ensure no broken links
- Check markdown renders correctly
- Verify code examples compile/run

## Output

```
DOCUMENTATION UPDATE
====================
Updated:
- README.md (setup instructions, new feature X)
- pkg/auth/doc.go (added GoDoc for AuthHandler)
- docs/api.md (new endpoint documentation)

Verified: All links valid, examples compile
```

**Execute documentation update now.**
