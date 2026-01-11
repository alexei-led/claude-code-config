---
context: fork
model: haiku
allowed-tools:
  - Task
  - Read
  - Glob
  - Grep
  - Bash(jq:*)
description: Audit spec documents for abstraction level violations
---

# Spec Audit

Analyze spec documents for abstraction level violations. Report-only, no modifications.

## Documentation Hierarchy

| Document            | Focus | Should Contain                            |
| ------------------- | ----- | ----------------------------------------- |
| `/docs/*.md`        | WHY   | Business context, architecture, decisions |
| `app_spec.txt`      | WHAT  | Requirements, success criteria            |
| `feature_list.json` | HOW   | Implementation steps, technologies        |

## Guardrails

- **Read-only**: Never modifies any files
- **Conservative**: When uncertain, marks as SUGGESTION not CRITICAL
- **Actionable**: Reports include specific line/section references

---

## Phase 1: Check for Spec Files

```bash
ls feature_list.json 2>/dev/null && echo "SPEC_EXISTS" || echo "NO_SPEC"
```

**If NO_SPEC**: Report "Not a spec-driven project. Run `/spec:init` to initialize." and stop.

---

## Phase 2: Spawn Auditor Agent

```
Task(
  subagent_type="spec-auditor",
  description="Audit abstraction levels",
  prompt="Analyze all spec documents for abstraction level violations:
  - Check docs/*.md for content that belongs in app_spec.txt or feature_list.json
  - Check app_spec.txt for implementation details (HOW in WHAT)
  - Check feature_list.json for requirements (WHAT in HOW)

  Return structured report with severity levels and suggested moves."
)
```

---

## Phase 3: Present Report

Display agent's report directly. Add summary:

```
## Audit Summary

**Status**: CLEAN | HAS_ISSUES
**Critical**: N items need immediate attention
**Suggestions**: M items could be improved

### Recommended Actions
1. <prioritized list of fixes>

Run `/spec:align` to reconcile code with spec after fixing abstraction issues.
```

---

**Execute now.**
