---
allowed-tools:
- Read
- Edit
- Write
- Grep
- Glob
argument-hint: '[topic] [--dry-run]'
description: Extract learnings and generate project-specific customizations (CLAUDE.md,
  CONTEXT.md, ADRs, commands, skills, hooks). Use when user says "learn", "extract
  learnings", "what did we learn", "save learnings", "adapt config", "capture domain
  language", or wants to improve Claude Code based on conversation patterns.
name: learning-patterns
---

<!-- Platform guidance for non-Claude models (Codex CLI, Gemini CLI) -->
<!-- Persistence: Keep going until the task is fully resolved. Do not stop at the first obstacle. -->
<!-- Tool use: Use available tools to verify — do not guess at file contents, paths, or command output. -->
<!-- Planning: Reflect between steps. Decompose complex problems into logical sub-steps before acting. -->
<!-- Reliability: Assess risk before irreversible actions. Ask for clarification on ambiguity. -->
<!-- Completeness: Generate complete responses without truncating. Review your output against the original constraints. -->

# Learn from Session

Extract actionable learnings and generate project-specific customizations. Adapts Claude Code to project patterns over time. Ground changes in actual conversation/tool output and ask one question at a time when confirmation is needed.

## Critical Routing Rules

- Use this skill only for durable project learning: reusable instructions, domain language, decisions, commands, skills, or hooks.
- Do not use it for ordinary documentation edits. Route README/API/docs updates to `documenting-code`; ask whether durable learning should also be captured only if the session reveals a reusable project rule.
- Do not fabricate learnings. If the conversation transcript or tool evidence is missing, say actual extraction is blocked and ask for the missing evidence before proposing permanent changes.
- If the user asks to describe the workflow, describe the phases and the evidence needed; do not apply changes.
- Treat secrets, credentials, local paths, one-off failures, and transient debugging details as non-durable unless the user explicitly says otherwise. Do not persist `/tmp/...` paths; preserve only the durable rule, such as "skill eval summaries are written under the configured skill-eval workspace".
- Always name the target artifact before proposing persistence, e.g. `AGENTS.md` for workflow rules, `CONTEXT.md` for domain language, `docs/adr/` for decisions, `.claude/commands/` for repeated commands, or `.claude/skills/` for complex workflows.


1. Discover existing customizations
2. Extract learnings from conversation
3. Categorize by artifact type
4. Distill to concrete artifacts
5. Deduplicate & merge with existing
6. Budget check
7. Present & confirm
8. Apply changes
9. Verify generated customization

---

## Phase 1: Discover Existing

Find ALL project customization files:

```bash
# Run these in parallel via Glob
.claude/CLAUDE.md OR CLAUDE.md          # Instructions
.claude/commands/*.md                    # Commands
.claude/skills/*/SKILL.md               # Skills
.claude/settings.json                    # Hooks
.claude/rules/*.md                       # Rules
CONTEXT.md / CONTEXT-MAP.md              # Domain language
docs/adr/*.md                            # Durable decisions
```

**Record counts** for budget tracking later.

---

## Phase 2: Extract Learnings

Analyze conversation for these signal types:

### Instruction Signals -> CLAUDE.md

| Signal             | Look For                                      |
| ------------------ | --------------------------------------------- |
| Corrections        | "no", "wrong", "actually...", "instead..."    |
| Direct guidance    | "always", "prefer", "use X", "never"          |
| Repeated explains  | Same thing clarified 2+ times                 |
| Project quirks     | Unexpected behaviors, edge cases, workarounds |
| Commands/workflows | Specific commands, sequences that worked      |

### Command Signals -> .claude/commands/

| Signal              | Look For                                 | Confidence |
| ------------------- | ---------------------------------------- | ---------- |
| Repeated task       | Same request 3+ times in session/history | HIGH       |
| "I always" pattern  | "I always run X before Y"                | HIGH       |
| Multi-step sequence | "first lint, then test, then build"      | MEDIUM     |
| Template request    | "create a new X like we discussed"       | MEDIUM     |
| Workflow mention    | "my workflow is X then Y then Z"         | HIGH       |

### Domain Signals -> CONTEXT.md / docs/adr/

| Signal               | Artifact     | Look For                                      |
| -------------------- | ------------ | --------------------------------------------- |
| Term resolution      | CONTEXT.md   | "call this X", "X means", overloaded jargon |
| Ambiguity resolved   | CONTEXT.md   | "not account, customer", "avoid Y"          |
| Durable trade-off    | ADR          | hard-to-reverse, surprising, real alternative |
| Scope rejection      | .out-of-scope | "we will not support X because..."          |

Only record domain concepts meaningful to domain experts. General implementation terms do not belong in `CONTEXT.md`.

### Skill Signals -> .claude/skills/

| Signal              | Look For                                        | Confidence |
| ------------------- | ----------------------------------------------- | ---------- |
| Complex multi-tool  | Workflow spanning 3+ files with analysis        | HIGH       |
| Agent orchestration | "spawn agents to check X and Y in parallel"     | HIGH       |
| Domain expertise    | Detailed tech discussion needing reference docs | MEDIUM     |
| Progressive need    | "for basic use X, for advanced see Y"           | MEDIUM     |

### Hook Signals -> .claude/settings.json

| Signal             | Look For                                 | Confidence |
| ------------------ | ---------------------------------------- | ---------- |
| Blocking rule      | "never do X", "always block Y"           | HIGH       |
| Validation need    | "always run linter after edit"           | HIGH       |
| Format requirement | "use prettier on save", "format on edit" | MEDIUM     |
| Approval pattern   | "ask before destructive commands"        | MEDIUM     |

**If `$ARGUMENTS` contains topic**: Extract ONLY learnings related to that topic.
**If `$ARGUMENTS` contains `--dry-run`**: Show what would be created, don't write.

---

## Phase 3: Categorize

Pick an explicit target artifact for every durable learning before drafting text. Do not merely say you will discover possible destinations; choose the destination and name it in the workflow.

- `AGENTS.md` / `CLAUDE.md` — reusable workflow or coding instructions
- `CONTEXT.md` — domain language and project glossary terms
- `docs/adr/NNNN-slug.md` — hard-to-reverse decisions with real alternatives
- `.claude/commands/{name}.md` — repeated command workflows
- `.claude/skills/{name}/SKILL.md` — complex reusable multi-tool workflows
- `.claude/settings.json` — hooks, permissions, or automation

If no target artifact is justified, do not persist the learning.

When the learning is a reusable project workflow, choose `AGENTS.md`/`CLAUDE.md`; when it is domain language, choose `CONTEXT.md`; when it is a hard-to-reverse decision, choose `docs/adr/`; when it is a repeated command sequence, choose `.claude/commands/`; when it is a reusable multi-tool process, choose `.claude/skills/`.

Sort extractions into buckets:

```
Instructions: [list of instruction candidates]
Domain docs: [CONTEXT.md / ADR / out-of-scope candidates]
Commands: [list of command candidates with names]
Skills: [list of skill candidates with names]
Hooks: [list of hook candidates with events]
```

**Apply confidence threshold**: Only include HIGH confidence for commands/skills/hooks.
MEDIUM confidence items go to instructions in CLAUDE.md instead.

---

## Phase 4: Distill to Artifacts

### Instructions -> CLAUDE.md format

| Pattern           | Example                                      |
| ----------------- | -------------------------------------------- |
| `Use X`           | Use prepared statements for SQL              |
| `Prefer X over Y` | Prefer explicit returns over bare err        |
| `When X -> do Y`  | When tests fail -> check CI logs first       |
| `X requires Y`    | Auth endpoints require Bearer token          |
| `Run: \`...\``    | Run: `kubectl rollout restart deploy/api`    |
| `Note: X`         | Note: `Get()` returns `nil, nil` when absent |

**One instruction per line. Max 80 chars.**

### Commands -> .claude/commands/{name}.md

```markdown
---
description: { 1-line description }
allowed-tools: { tools needed, e.g., Bash(make *), Read }
argument-hint: { optional args }
---

# {Command Name}

{Brief purpose}

## Steps

1. {step from conversation}
2. {step from conversation}

## Context

{Any relevant @ references or bash context}
```

### Domain Docs

`CONTEXT.md` entries:

```markdown
**Term**:
One-sentence definition.
_Avoid_: overloaded synonym, fuzzy alias
```

ADR entries under `docs/adr/NNNN-slug.md`:

```markdown
# Decision title

One to three sentences: context, decision, why.
```

Write ADRs only when the decision is hard to reverse, surprising without context, and a real trade-off.

Out-of-scope records under `.out-of-scope/<concept>.md` capture rejected enhancements with reasoning and prior requests.

### Skills -> .claude/skills/{name}/SKILL.md

```markdown
---
name: { kebab-case-name }
description: { when to use, triggers }
user-invocable: true
context: fork
allowed-tools: { restrictions if any }
---

# {Skill Name}

{Purpose}

## When to Use

- {scenario 1}
- {scenario 2}

## Workflow

1. {step 1}
2. {step 2}
```

### Skill Authoring Rules

- Description must explain what the skill does and when to use it.
- Prefer `SKILL.md` under ~150 lines.
- Move deep reference material to sibling files.
- Add scripts for deterministic repeated operations.
- Keep one level of references; nested docs become a treasure hunt without the treasure.
- Use specific triggers, not "helps with things" mush.

### Hooks -> settings.json addition

```json
{
  "EventType": [
    {
      "matcher": "ToolPattern",
      "hooks": [
        {
          "type": "command",
          "command": "command-here",
          "timeout": 30
        }
      ]
    }
  ]
}
```

**Default to PostToolUse** (non-blocking) unless explicit blocking requirement.

---

## Phase 5: Deduplicate & Merge

For each artifact type:

1. **Read existing** if file exists
2. **Find overlaps** by topic/name
3. **Merge strategy**:

| Scenario                   | Action                                 |
| -------------------------- | -------------------------------------- |
| New adds specificity       | Update existing with concrete details  |
| New adds example           | Append example to existing             |
| Both have value            | Combine into single comprehensive item |
| New is subset of existing  | Keep existing, skip new                |
| Name collision (cmd/skill) | Merge content into existing file       |

**Prefer updating existing over creating new.**

---

## Phase 6: Budget Check

Recommended limits:

| Artifact    | Limit     | Why                   |
| ----------- | --------- | --------------------- |
| CLAUDE.md   | 200 lines | Context efficiency    |
| CONTEXT.md  | concise   | Domain terms only     |
| ADRs        | sparse    | Decisions, not diary  |
| Commands    | 10        | Discoverability       |
| Skills      | 5         | Complexity management |
| Hooks       | 5         | Debugging simplicity  |

If exceeding budget:

1. Propose consolidations
2. Identify stale items for removal
3. Warn but allow user to proceed

---

## Phase 7: Present & Confirm

Show ALL proposed changes:

```markdown
## Proposed Changes

### CLAUDE.md (instructions)

Target: `.claude/CLAUDE.md`
Lines: X/200

**Updates:**

- [old] -> [merged]

**Additions:**

- New instruction

### Commands

- `/pre-commit` - Run checks before commit
  -> `.claude/commands/pre-commit.md`

### Skills

~ `auth-patterns` - Updated with OAuth2 flow
-> `.claude/skills/auth-patterns/SKILL.md`

### Hooks

- PostToolUse[Edit|Write]: Run prettier
  -> `.claude/settings.json`

---

Rollback: `git checkout .claude/`
```

**STOP**:


If "Select items": Show multi-select for each category.

---

## Phase 8: Apply

Based on confirmation:

1. **CLAUDE.md**: Edit existing lines, add new at appropriate sections
2. **Commands**: Write new .md files, edit existing for merges
3. **Skills**: Create directory + SKILL.md, add reference files if needed
4. **Domain docs**: Update `CONTEXT.md`, ADRs, or `.out-of-scope/` only for durable knowledge
5. **Hooks**: Merge into existing settings.json `hooks` object

## Phase 9: Verify Generated Customization

Always include verification in the workflow, even when only describing what would happen. Review every changed artifact before reporting success:

1. Re-read the changed `AGENTS.md`/`CLAUDE.md`, `CONTEXT.md`, ADR, command, skill, or hook file.
2. Check the generated customization is specific, non-duplicative, and grounded in session evidence.
3. For commands/hooks/skills, verify frontmatter, paths, and referenced commands are valid when practical.
4. Report verification results and any skipped checks with reasons.

### Section Placement (CLAUDE.md)

| Section    | Content                          |
| ---------- | -------------------------------- |
| Patterns   | Architecture, naming, structure  |
| Code Style | Formatting, idioms, conventions  |
| Workflows  | Build, test, deploy commands     |
| Gotchas    | Edge cases, quirks, known issues |

---

## Output

```
LEARNED
=======
Target: .claude/

Instructions: (CLAUDE.md)
  ~ "Use error wrapping" -> "Wrap errors: fmt.Errorf(\"op: %w\", err)"
  + "Note: API returns nil, nil when absent"

Commands: (commands/)
  + /pre-commit - Run lint, test, build

Skills: (skills/)
  + auth-patterns - OAuth2 and JWT handling

Domain docs:
  + CONTEXT.md: "Materialization" term
  + docs/adr/0003-use-events-for-materialization.md

Hooks: (settings.json)
  + PostToolUse[Edit]: prettier --write

Budget: 45/200 instructions | concise context | sparse ADRs | 3/10 commands | 1/5 skills | 1/5 hooks
```

---

## Edge Cases

- **Empty session**: "No learnings detected. Try after a longer conversation."
- **All low confidence**: Convert to CLAUDE.md instructions instead
- **No .claude/ directory**: Create it with user permission
- **--dry-run flag**: Show output but skip Phase 8

---
