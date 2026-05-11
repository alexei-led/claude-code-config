---
name: learning-patterns
description: Extract durable learnings from a session and propose project customizations — agent-instructions file, CONTEXT.md, ADRs, project skills, hooks. Use when the user says "learn", "extract learnings", "what did we learn", "save learnings", "adapt config", "capture domain language", or wants to encode session patterns durably.
---

# Learn from Session

Extract actionable, durable learnings and propose project-specific customizations. Ground every change in actual conversation or tool evidence. Ask one question at a time when confirmation is needed.

## Routing

- Use only for durable project learning: reusable instructions, domain language, decisions, commands, skills, hooks.
- Documentation edits route to `documenting-code`.
- Do not fabricate. If evidence is missing, say extraction is blocked and ask for it.
- Secrets, credentials, local paths, transient debugging details, and one-off failures are non-durable unless the user explicitly says otherwise.
- Always name the exact target artifact before proposing persistence.

## Workflow

1. Discover existing customizations
2. Extract learnings from the conversation
3. Categorize by artifact type
4. Distill to concrete artifacts
5. Deduplicate against existing
6. Budget check
7. Present and confirm
8. Apply approved changes
9. Verify each changed file

If the user passed a topic, scope extraction to that topic. If the user passed `--dry-run`, run Phases 1–7 only.

## Phase 1: Discover

Read existing customization files. Default portable paths (adapt to the platform's conventional locations):

- `AGENTS.md` — agent instructions / project memory
- `.agents/skills/*/SKILL.md` — project skills
- `.agents/agents/*.md` — project subagents
- `.agents/commands/*.md` — project commands
- `CONTEXT.md`, `CONTEXT-MAP.md` — domain language
- `docs/adr/*.md` — durable decisions
- `.out-of-scope/*.md` — rejected scope with reasoning

Record counts for the budget check.

## Phase 2: Extract

Scan the conversation for these signal types.

Instruction signals → agent-instructions file:

- Corrections: "no", "wrong", "actually", "instead"
- Direct guidance: "always", "prefer", "use X", "never"
- Repeated explanations of the same point
- Project quirks: unexpected behavior, edge cases, workarounds
- Workflow sequences that consistently worked

Domain signals:

- Term resolution → `CONTEXT.md` ("call this X", "X means", overloaded jargon)
- Ambiguity resolved → `CONTEXT.md` ("not account, customer", "avoid Y")
- Hard-to-reverse trade-off → `docs/adr/` (surprising, real alternative)
- Scope rejection → `.out-of-scope/` ("we will not support X because")

Skill signals → project skills directory. Promote to a skill only when the workflow is repeated or likely to recur, multi-step enough to forget details, tool-heavy or evidence-heavy, and specific enough to trigger reliably. Prefer updating an existing skill over creating a duplicate.

Hook signals → settings:

- Blocking rule ("never do X", "always block Y") — HIGH confidence
- Validation hook ("always run linter after edit") — HIGH
- Format requirement ("use prettier on save") — MEDIUM
- Approval pattern ("ask before destructive commands") — MEDIUM

Only HIGH-confidence items become skills or hooks. MEDIUM items become single-line entries in the agent-instructions file instead.

## Phase 3: Categorize

Pick exactly one target artifact per learning before drafting text:

- Reusable workflow or coding instruction → agent-instructions file (`AGENTS.md`)
- Domain term → `CONTEXT.md`
- Hard-to-reverse decision with real trade-off → `docs/adr/NNNN-slug.md`
- Repeated multi-step workflow → `.agents/skills/<name>/SKILL.md`
- Blocking, validation, or approval automation → settings/hooks (platform-specific)
- Rejected feature with reasoning → `.out-of-scope/<concept>.md`

If no target is justified, drop the learning.

## Phase 4: Distill

Agent-instructions entries — one-line rules, ~80 chars max:

- `Use X for Y.`
- `Prefer X over Y.`
- `When X, run Y.`
- `Never X without confirmation.`
- ``Run: `<command>``.``
- ``Note: `<surprise>``.``

CONTEXT.md entry shape:

```markdown
**Term**:
One-sentence definition.
_Avoid_: overloaded synonym.
```

ADR entry shape (`docs/adr/NNNN-slug.md`):

```markdown
# Decision title

Context, decision, why — one to three sentences.
```

Write ADRs only when the decision is hard to reverse, surprising without context, and has a real alternative.

Out-of-scope entry: capture rejected enhancements with reasoning and any prior requests so the same idea is not re-litigated.

Project skill: follow [agentskills.io](https://agentskills.io/specification). Required `name` and `description` frontmatter + markdown body. Description must state what the skill does and concrete trigger phrases. Body under ~150 lines; deep references go in sibling files. Vendor-neutral instructions, no platform-specific tool names.

## Phase 5: Deduplicate

Read each existing artifact and look for overlaps. Merge rules:

- New adds specificity → update existing with concrete details.
- New adds an example → append to existing.
- Both have value → combine into one item.
- New is subset of existing → skip.
- Name collision → merge into existing file.

Prefer updating existing over creating new.

## Phase 6: Budget check

Recommended limits:

- Agent-instructions file: ~200 lines (context efficiency)
- `CONTEXT.md`: concise — domain terms only
- ADRs: sparse — decisions, not diary
- Skills: ~5 user-invocable per project for discoverability
- Hooks: ~5 for debugging simplicity

Over budget → propose consolidations or stale removals before adding more.

## Phase 7: Present and confirm

Show all proposed changes grouped by target file. Use `+` for additions, `~` for updates. Include the rollback command (typically `git checkout`).

Ask one question for approval: apply all / select items / edit first / no. For "select items", show one selector per category.

## Phase 8: Apply

- Agent-instructions file: edit existing lines or append in the appropriate section.
- `CONTEXT.md`, ADRs, out-of-scope: write or edit.
- Skills: create directory + `SKILL.md`, plus supporting files when needed.
- Hooks: merge into existing settings.

## Phase 9: Verify

Re-read every changed file. Check:

- Specific, non-duplicative, grounded in session evidence.
- Frontmatter and paths valid.
- Referenced commands resolvable when practical.
- Generated skill follows agentskills.io rules.

Report verification results and any skipped checks with reasons.

## Output

```text
LEARNED

Instructions: +N ~N
Domain docs: +N ~N
Skills: +N ~N
Hooks: +N ~N

Applied:
- file — change

Verification:
- check — pass/fail
```

## Edge cases

- Empty session → "No learnings detected. Try after a longer conversation."
- All low-confidence items → bundle as instructions in the agent-instructions file.
- No customization directories yet → ask before creating them.
- `--dry-run` → run Phases 1–7, skip 8, still show what would change.
