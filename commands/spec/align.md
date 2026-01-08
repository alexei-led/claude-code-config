---
context: fork
allowed-tools:
  - Task
  - TaskOutput
  - TodoWrite
  - Read
  - Write
  - AskUserQuestion
  - Glob
  - Grep
  - Bash(jq:*)
  - Bash(git status:*)
  - Bash(git log:*)
description: Align spec with code implementation (bottom-up)
---

# Spec Align

Discover what code implements and align feature_list.json with reality (bottom-up).

**Use TodoWrite** to track these 5 phases:

1. Code discovery
2. Gap analysis
3. Propose changes
4. User approval
5. Apply updates

## Documentation Hierarchy

| Layer   | Document            | Focus                 |
| ------- | ------------------- | --------------------- |
| WHAT    | `app_spec.txt`      | Requirements          |
| HOW     | `feature_list.json` | Implementation tasks  |
| REALITY | Code + Tests        | What's actually built |

**Direction**: code → feature_list → app_spec (bottom-up)

## Guardrails

- **Add-only**: Never modify existing feature descriptions (immutability)
- **Deprecate, don't delete**: Orphaned features get `deprecated: true`
- **User approval**: All changes require explicit approval
- **Conservative**: Ambiguous cases flagged for human review

---

## Phase 1: Discovery (Background)

**Spawn `spec-aligner` agent in background:**

```
Task(
  subagent_type="spec-aligner",
  run_in_background=true,
  description="Discover code vs spec gaps",
  prompt="Analyze codebase and compare against feature_list.json:
  1. Discover implemented functionality using semantic search and structural analysis
  2. Compare against feature_list.json entries
  3. Identify: undocumented features, orphaned specs, drifted steps
  4. Return structured alignment report with proposed changes"
)
```

---

## Phase 2: Collect & Present Gaps

**Collect discovery results:**

```
TaskOutput(task_id=<aligner_agent_id>, block=true)
```

**Present summary to user** (10 lines max):

```
## Alignment Analysis

**Features in Spec**: N
**Features in Code**: M (estimated)

**Gaps Found**:
- Undocumented: X features in code not in spec
- Orphaned: Y features in spec not in code
- Drifted: Z features with mismatched steps

Ready to review proposed changes?
```

**STOP**: Use `AskUserQuestion` - "Review proposed changes? [Show details / Apply all / Skip]"

---

## Phase 3: Propose Changes

**If user wants details**, present each category:

### Undocumented Features (to add)

```
| # | Discovered Feature | Proposed Category | Confidence |
|---|-------------------|-------------------|------------|
| 1 | Password reset flow | core | HIGH |
| 2 | Rate limiting | integration | MEDIUM |
```

### Orphaned Features (to deprecate)

```
| # | Feature | Description | Reason |
|---|---------|-------------|--------|
| 1 | Feature #5 | "Admin dashboard" | No implementation found |
```

### Drifted Features (for awareness)

```
| Feature | Spec Says | Code Does |
|---------|-----------|-----------|
| Auth | "Use session tokens" | Uses JWT |
```

---

## Phase 4: User Approval

**STOP**: Use `AskUserQuestion` for each category:

1. "Add these undocumented features to spec? [All / Select / None]"
2. "Mark these orphaned features as deprecated? [All / Select / None]"

If user selects "Select", present numbered list for individual approval.

---

## Phase 5: Apply Updates

**For approved additions:**

Read current feature_list.json, append new features:

```bash
jq '. + <new_features_array>' feature_list.json > tmp && mv tmp feature_list.json
```

**For approved deprecations:**

Update features with `deprecated: true`:

```bash
jq '.[<index>].deprecated = true' feature_list.json > tmp && mv tmp feature_list.json
```

**Update `claude-progress.txt`:**

```
## Alignment Session

**Action**: Bottom-up spec alignment
**Added**: N new features
**Deprecated**: M orphaned features
**Progress**: X/Y features (Z%)

**Next**: Run /spec:audit to check abstraction levels
```

---

## Phase 5.5: App Spec Updates (if needed)

If undocumented features require app_spec.txt changes:

**STOP**: Use `AskUserQuestion` - "Update app_spec.txt with new requirements? [Show diff / Apply / Skip]"

Only add new sections/requirements, never modify existing content.

---

## Summary

Present alignment summary to user:

```
## Alignment Complete

**Added**: N features to feature_list.json
**Deprecated**: M features marked deprecated
**Progress**: X/Y → A/B features (Z%)

### Next Steps
1. Run /spec:audit to check abstraction levels
2. Run /spec:sync to verify implementation status
3. Run /spec:work to continue development
```

---

**Execute now.**
