---
allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - AskUserQuestion
description: Extract strategic learnings from session and update project CLAUDE.md
argument-hint: [topic]
---

# Learn from Session

Extract concise, actionable instructions from session. Optimize for future Claude context efficiency.

## Target File

Find in order: `.claude/CLAUDE.md` → `CLAUDE.md` → ask user which to create.

## Phase 1: Extract Learnings

Analyze conversation for:

| Signal             | Look For                                          |
| ------------------ | ------------------------------------------------- |
| Corrections        | "no", "wrong", "actually...", "instead..."        |
| Direct guidance    | "always", "prefer", "use X"                       |
| Repeated explains  | Same thing clarified 2+ times                     |
| Project quirks     | Unexpected behaviors, edge cases, workarounds     |
| Commands/workflows | Specific commands, sequences, scripts that worked |

**If `$ARGUMENTS` provided**: Extract ONLY learnings related to that topic.

## Phase 2: Distill to Minimum Viable Instructions

**Goal**: Maximum signal, minimum tokens. Frame positively.

### Instruction Patterns

| Pattern           | Example                                      |
| ----------------- | -------------------------------------------- |
| `Use X`           | Use prepared statements for SQL              |
| `Prefer X over Y` | Prefer explicit returns over bare err        |
| `When X → do Y`   | When tests fail → check CI logs first        |
| `X requires Y`    | Auth endpoints require Bearer token          |
| `Run: \`...\``    | Run: `kubectl rollout restart deploy/api`    |
| `Note: X`         | Note: `Get()` returns `nil, nil` when absent |

**One instruction per line. Max 80 chars when possible.**

## Phase 3: Deduplicate & Merge

Before adding to CLAUDE.md:

1. **Read existing file** - Understand current structure and content
2. **Find overlaps** - Search for instructions covering similar topics
3. **Merge intelligently** - Combine existing + new into improved version

### Merge Strategy

When new instruction overlaps with existing:

```markdown
# Existing in CLAUDE.md:

- Use error wrapping

# New from session:

- Wrap errors with fmt.Errorf and %w verb

# Merged result (update existing):

- Wrap errors: `fmt.Errorf("op: %w", err)`
```

| Scenario                  | Action                                 |
| ------------------------- | -------------------------------------- |
| New adds specificity      | Update existing with concrete details  |
| New adds example          | Append example to existing instruction |
| Both have value           | Combine into single comprehensive line |
| New is subset of existing | Keep existing, skip new                |
| Existing is outdated      | Replace existing with new              |

**Prefer updating existing instructions over adding new lines.**

## Phase 4: Size Check

**CLAUDE.md budget**: ~200 lines / ~8KB max recommended.

If file exceeds budget:

1. Identify stale instructions for removal
2. Propose consolidations of related items
3. Suggest trimming verbose sections

```bash
wc -l CLAUDE.md  # check lines
```

## Phase 5: Present & Confirm

Show proposed changes:

```markdown
## Proposed: [Topic or "Session Learnings"]

**Updates:**

- [existing line] → [merged version]

**Additions:**

- New instruction

Target: `path/to/CLAUDE.md`
Lines: total Y/200
```

**STOP**: Use `AskUserQuestion`:

| Header | Question               | Options                                    |
| ------ | ---------------------- | ------------------------------------------ |
| Action | Apply these learnings? | Append all / Review each / Edit first / No |

## Phase 6: Apply

1. **Update existing** - Edit lines that were merged
2. **Add new** - Insert truly new instructions
3. **Match sections** - Add to existing section if relevant
4. **Place strategically** - Frequent/important instructions near top

### Standard Sections

| Section    | Content                          |
| ---------- | -------------------------------- |
| Patterns   | Architecture, naming, structure  |
| Code Style | Formatting, idioms, conventions  |
| Workflows  | Build, test, deploy commands     |
| Gotchas    | Edge cases, quirks, known issues |

## Output

```
LEARNED
=======
Target: .claude/CLAUDE.md
Size: Y lines (Z% of budget)

Updated:
~ old → new

Added:
+ instruction
```

## Example Session

**Session learning**: "wrap errors with context using %w"

**Existing in CLAUDE.md**: "- Use error wrapping"

**Result**: Update existing line:

```
~ Use error wrapping → Wrap errors: `fmt.Errorf("op: %w", err)`
```

---

**Execute now. Extract learnings, find overlaps in existing CLAUDE.md, propose merges and additions.**
