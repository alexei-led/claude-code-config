---
allowed-tools: Task
description: Quick progress check for spec-driven development
---

# Spec-Driven Development Status

Spawn an **Explore** agent (subagent_type: Explore) with this prompt:

```
Gather spec-driven development project status:

1. Run feature progress commands:
   - `jq length feature_list.json`
   - `jq '[.[] | select(.passes == true)] | length' feature_list.json`
   - `jq '[.[] | select(.passes == false)] | length' feature_list.json`

2. Run: `git log --oneline -5`

3. Read: `claude-progress.txt`

4. Calculate: passing/total percentage, estimate remaining sessions

Return concise status:

SPEC STATUS
===========
Features: X/Y passing (Z%)
Recent commits: [list]
Last session: [summary]
Estimated remaining: ~N sessions
```

Display the agent's status report to the user.
