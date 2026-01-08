---
allowed-tools:
  - Task
  - TaskOutput
  - Read
  - AskUserQuestion
  - Bash(jq:*)
  - Bash(git status:*)
  - Bash(git log:*)
description: Sync feature_list.json and progress from code state and git history
---

# Spec Sync

Reconcile tracking files with actual code state after interrupted sessions.

Claude 4.5 excels at discovering state from the filesystem. This command leverages that capability—reading code, tests, and git history to determine true feature status rather than relying on potentially stale progress notes.

## Guardrails

- **Conservative**: When evidence is ambiguous, leave as `"passes": false`
- **Evidence-based**: Verify with code/tests, not just commit messages
- **Passes-only**: Preserve feature descriptions exactly. Only modify `"passes"` field.

---

## Phase 1: Discovery (Background)

**Spawn `spec-discover` agent in background:**

```
Task(
  subagent_type="spec-discover",
  run_in_background=true,
  prompt="Full discovery for sync - include discrepancies between claimed progress and feature_list.json state"
)
```

## Phase 2: Identify Discrepancies

**Collect discovery results:**

```
TaskOutput(task_id=<discovery_agent_id>)
```

From the discovery:

1. Parse features marked `passes: false` that progress file claims are done
2. Parse features with implementation evidence (commits, code) but marked false

## Phase 3: Parallel Verification

**For each suspected completion, spawn `spec-verifier` agent in parallel:**

```
Task(
  subagent_type="spec-verifier",
  run_in_background=true,
  prompt="Verify feature: <feature description>\nSteps: <steps array>"
)
```

Spawn ALL verification agents in a single message for parallel execution.

## Phase 4: Collect & Update

**Collect all verification results:**

```
TaskOutput(task_id=<verifier_1_id>)
TaskOutput(task_id=<verifier_2_id>)
...
```

For each verified feature:

- If verdict is YES: Update `feature_list.json` with `"passes": true`
- If verdict is NO: Leave unchanged, note what's missing

## Phase 5: Report

Update `claude-progress.txt`:

- Session type: "Sync Recovery"
- Features verified complete (list)
- Discrepancies found
- Current progress: X/Y passing (Z%)

Present sync summary to user:

```
## Sync Complete

**Updated**: N features marked as passing
**Unchanged**: M features (insufficient evidence)
**Progress**: X/Y → A/B passing

### Changes Made
- Feature 1: verified, marked passing
- Feature 2: verified, marked passing

### Still Failing (need work)
- Feature 3: missing tests
- Feature 4: partial implementation
```
