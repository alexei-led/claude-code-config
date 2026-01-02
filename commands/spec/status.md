---
allowed-tools: Task
description: Quick progress check for spec-driven development
---

# Spec Status

Quick snapshot of spec-driven development progress.

Spawn **Explore** agent (Task with subagent_type: Explore) to gather and report:

```
Spec-driven development status check:

1. Read `claude-progress.txt` first - last session summary, what's next
2. Query `feature_list.json`:
   - Total: `jq length feature_list.json`
   - Passing: `jq '[.[] | select(.passes == true)] | length' feature_list.json`
   - Failing: `jq '[.[] | select(.passes == false)] | length' feature_list.json`
3. Run `git log --oneline -5` for recent commits

Return concise report:
- Progress: X/Y passing (Z%)
- Last session: [from claude-progress.txt]
- Next recommended: [from claude-progress.txt or highest priority failing feature]
- Estimated remaining: ~N sessions at current pace
```

Display the agent's report.
