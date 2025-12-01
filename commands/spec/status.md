---
allowed-tools: Bash(cat:*), Bash(grep:*), Bash(wc:*), Bash(git log:*), Bash(jq:*), Read
description: Quick progress check for spec-driven development
---

# Spec-Driven Development Status

Show current progress on spec-driven development project.

## Check These Items

1. **Feature Progress** - Count passing vs failing tests:

   ```bash
   # Total features
   jq length feature_list.json

   # Passing
   jq '[.[] | select(.passes == true)] | length' feature_list.json

   # Failing
   jq '[.[] | select(.passes == false)] | length' feature_list.json
   ```

2. **Recent Activity** - Show last 5 commits:

   ```bash
   git log --oneline -5
   ```

3. **Progress Notes** - Read session summary:

   ```bash
   cat claude-progress.txt
   ```

4. **Calculate Completion**:
   - Passing / Total = completion percentage
   - Estimate remaining sessions based on average features per session

## Output Format

```
SPEC STATUS
===========
Features: X/Y passing (Z%)
Recent commits: [list]
Last session: [summary from claude-progress.txt]
Estimated remaining: ~N sessions
```

Run these checks and report status.
