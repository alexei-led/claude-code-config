---
allowed-tools: Task, Edit, Write, TodoWrite
description: Sync feature_list.json and progress from code state and git history
---

# Spec Sync

Reconcile tracking files with actual code state after interrupted sessions.

## Guardrails

- **Conservative**: When in doubt, leave as `"passes": false`
- **Evidence-based**: Commit messages are hints, not proof - verify with code/tests
- **Passes-only**: Only modify `"passes"` field in `feature_list.json`
- **Never**: Remove, reorder, edit descriptions, or add features

---

## Phase 1: Gather Evidence

Spawn **Explore** agent (Task with subagent_type: Explore, thoroughness: very thorough):

```
Analyze spec-driven project for discrepancies between tracking and reality:

1. Read `claude-progress.txt` first - what was claimed done last session
2. Read `feature_list.json` - current tracked state
3. Git analysis:
   - `git log --oneline -30`
   - `git log --since="3 days ago" --oneline`
   - Look for commits mentioning features, fixes, implementations
4. Count features:
   - Total: `jq length feature_list.json`
   - Passing: `jq '[.[] | select(.passes == true)] | length' feature_list.json`
5. Identify main source directories and key implementation files

Return:
- Discrepancies: features marked false that evidence suggests are done
- Evidence type for each: commit message, code exists, tests pass
- Current progress: X/Y passing (Z%)
- What claude-progress.txt says was last worked on
```

---

## Phase 2: Verify and Update

For each suspected completion:

1. Create TodoWrite to track verification progress
2. Read feature's `steps` from `feature_list.json`
3. Check implementation: search code, check tests exist
4. For UI features: use `/test:e2e` with screenshots
5. Only mark `"passes": true` with clear evidence

Update `claude-progress.txt`:

- Session type: "Sync Recovery"
- Features verified complete
- Discrepancies found
- Current progress
- Next recommended work

---

## Phase 3: Report

Present sync summary:

- Changes made (N features updated)
- Evidence for each verification
- Features left unchanged (with reasons)
- Current progress: X/Y passing (Z%)
- Recommended next steps
