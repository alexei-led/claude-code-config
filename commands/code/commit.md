---
context: fork
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git status:*)
description: Group changes logically and create bundled commits with concise messages
---

# Smart Commit

Group changed files logically and create focused, atomic commits.

**Use TodoWrite** to track these 4 phases:

1. Spawn analysis agents
2. Collect groupings and style
3. Execute commits
4. Present summary

**Main context = orchestration only. All analysis in background agents.**

---

## Phase 1: Spawn Analysis Agents

**Spawn TWO background agents in a single message:**

```
Task(
  subagent_type="general-purpose",
  run_in_background=true,
  model="haiku",
  description="Git changes analysis",
  prompt="""
Analyze changes and propose groupings. Output ONLY JSON, no explanation.

Run:
- git status --porcelain
- git diff --name-status HEAD

Group by: feature (impl+tests), fix (bug+test), refactor, docs, config/infra

Output format (ONLY this, nothing else):
{"groups":[{"files":["path1","path2"],"type":"feature|fix|refactor|docs|config"}],"empty":false}

If no changes: {"empty":true}
"""
)

Task(
  subagent_type="general-purpose",
  run_in_background=true,
  model="haiku",
  description="Commit style guide",
  prompt="""
Get recent commit style. Output ONLY JSON, no explanation.

Run: git log --oneline -8

Analyze style: prefix pattern, tense, length, scope format.

Output format (ONLY this, nothing else):
{"style":"<one-line description>","examples":["msg1","msg2"]}
"""
)
```

## Phase 2: Collect & Merge

```
TaskOutput(task_id=<changes_agent_id>, block=true)
TaskOutput(task_id=<style_agent_id>, block=true)
```

**If empty=true:** "Nothing to commit" → stop.

**Merge results internally** - draft commit messages matching the style for each group.

## Phase 3: Execute Commits

For each group:

```bash
git add <files>
git commit -m "$(cat <<'EOF'
<message matching style>
EOF
)"
```

## Phase 4: Summary

```bash
git status
```

Present (3-5 lines max):

- Commits created: N
- Each: `<hash short> <message>`
- Remaining uncommitted (if any)

---

**Execute now.**
