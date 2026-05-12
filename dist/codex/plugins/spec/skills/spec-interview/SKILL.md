---
description: Capture PRD-quality requirements through structured Q&A. Use when a new
  requirement needs deep exploration — produces a `REQ-*.md` via 8–15 targeted questions.
name: spec-interview
---

# `spec interview` — deep requirement extraction

CLI at `scripts/specctl`. Extract complete requirements through structured Q&A. Produces PRD-quality `REQ-*.md`. Input is an idea text, a doc path, or an existing `REQ-id` to refine.

## Step 1: Load context

- If input is a `REQ-id`: run `scripts/specctl show <REQ-id>` and read the file. Interview to refine.
- If input is a file path: read it. Use content as starting context.
- If input is idea text: start fresh.
- If empty: ask "What feature or requirement would you like to explore?"

### Before questions: load durable project context

Read when present:

- `CONTEXT.md`, `CONTEXT-MAP.md` — domain language
- `docs/adr/*.md` — architectural decisions
- `.out-of-scope/*.md` — rejected enhancements

If the new requirement resembles an `.out-of-scope/` record, surface it: "This resembles a previously rejected concept because <X>. Reconsider, narrow scope, or stop?"

Use the domain vocabulary from `CONTEXT.md`. If the user uses an overloaded term, resolve it before writing the REQ.

## Step 2: Interview process

**Ask one question at a time** using the runtime's multi-choice / structured-question mechanism. Do not output questions as plain prose paragraphs — use the structured question facility so answers are clean to parse.

Plan for 8–15 questions in total; go longer only for genuinely complex requirements. Stop when success criteria, scope, constraints, and blockers are clear.

### Question categories (ask in this order, adapt based on answers)

**1. Problem & scope** (5–8)

- What problem does this solve?
- Who experiences this problem?
- How painful is it today (workarounds)?
- What's in scope vs explicitly out of scope?
- Is this a new capability or improving existing?

**2. Users & stakeholders** (4–6)

- Primary users? Secondary users (admin, support)?
- What do users need to accomplish?
- How do they do it today?
- Accessibility requirements?

**3. Success criteria** (5–8)

- What does "done" look like?
- How will users know it works?
- Performance / scale requirements?
- Compliance / regulatory requirements?

**4. Constraints** (4–6)

- Technical (must use X, can't use Y)?
- Business (timeline, budget, dependencies)?
- Compatibility (browsers, devices, APIs)?
- Security (auth, data protection)?

**5. Edge cases & failures** (6–10)

- Invalid input behavior?
- Offline / disconnected?
- External service down?
- User cancels mid-operation?
- Error states and communication?
- Rate-limiting / abuse concerns?

**6. Data & state** (4–6)

- What data is needed? Where does it come from?
- Effects on existing data?
- Retention / deletion?
- Privacy considerations?

**7. Unknowns & risks** (3–5)

- Most uncertain area?
- What could derail this?
- What needs research first?
- Dependencies on other work?

### Interview guidelines

- Ask non-obvious questions; assume technical competence.
- Dig deep on answers; follow up on interesting points.
- Surface hidden complexity (things the user might not have considered).
- Probe contradictions when answers don't align.
- Use multi-select for non-exclusive options.
- Stop when complete — don't pad.

## Step 3: Write `REQ-*.md`

### Generate REQ id

If new: pick a descriptive slug (e.g., `REQ-auth`, `REQ-notifications`, `REQ-export`).

### Template

```markdown
---
id: REQ-<slug>
version: 1
priority: <critical|normal|low>
created: <date>
---

# <Title>

## Problem

<Clear problem statement from interview>

## Users

- **Primary**: <who>
- **Secondary**: <who, if any>

## Success criteria

- [ ] <criterion 1>
- [ ] <criterion 2>

## Constraints

- <constraint 1>

## Edge cases

- <edge case>: <expected behavior>

## Data requirements

- <what data is needed>
- <where it comes from>

## Open questions

- <unresolved items needing research>

## Implementation decisions

- <modules/interfaces likely touched, if known>

## Testing decisions

- <critical behaviors to test>
- <public interfaces or integration seams to verify>
- <edge/error cases that matter>

## Out of scope

- <explicitly excluded items>

## Domain language

- <terms resolved or added to CONTEXT.md>

## Prior decisions and rejections

- <relevant ADRs or .out-of-scope records>
```

### Write the file

```bash
mkdir -p .spec/reqs
```

Write `.spec/reqs/REQ-<slug>.md`. If refining, edit specific sections.

## Step 4: Completion

Show summary:

- Questions asked: <count>
- Key decisions captured
- Out-of-scope items captured
- Domain terms resolved
- File written: `.spec/reqs/REQ-<slug>.md`

Suggest:

```
Requirement captured. Next steps:
1. Create implementation plan: use the `spec-plan` skill — `spec-plan REQ-<slug>`
2. Refine further: use the `spec-interview` skill — `spec-interview REQ-<slug>`
3. View status: use the `spec-status` skill
```

## Not in scope (defer to `spec plan`)

- File/line references
- Task creation
- Task sizing (S / M / L)
- Implementation approach
- Dependency ordering

Interview captures WHAT / WHY. `spec plan` captures HOW.
