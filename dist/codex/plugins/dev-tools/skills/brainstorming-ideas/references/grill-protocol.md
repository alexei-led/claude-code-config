# Grill Protocol

Interview the user about every decision branch in the plan until every node is resolved or explicitly deferred. Walk the decision tree depth-first. For each question, give your own recommended answer before waiting for theirs.

Ask one question at a time.

If a question can be answered by reading the codebase, read it first — then ask only what the code doesn't settle.

## Phase order

1. **Scope** — problem framing, goals, explicit non-goals (2–3 questions)
2. **Decisions** — key design choices, dependencies between them, constraints (most questions)
3. **Edge cases** — failure modes, rollback, scale limits (close out)

## Per-question format

```
Q{n}: [question]
→ My take: [your recommendation and why]
```

## Final summary

When all branches are resolved or explicitly deferred, emit:

```
GRILL COMPLETE
==============
Locked:
- [decision]: [outcome]

Deferred:
- [item]: [reason]

Constraints surfaced:
- [constraint]
```

## Failure handling

- **Plan too vague** — ask for the plan first; do not invent decisions to grill on.
- **User deflects** — restate the same question; do not move to the next until this one is answered or explicitly deferred.
- **Codebase contradicts a stated assumption** — surface the discrepancy and resolve it before continuing.
- **Scope creep during grilling** — note the new topic as a deferred item; finish the current branch first.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT).
