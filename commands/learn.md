---
allowed-tools: Read, Edit, Write, Grep, Glob, AskUserQuestion
description: Extract strategic learnings from session and update project CLAUDE.md
argument-hint: [topic]
---

# Learn from Session

Extract actionable learnings from current session and update project-level CLAUDE.md.

## Target File Detection

Find target in order:

1. `.claude/CLAUDE.md` (project-local)
2. `CLAUDE.md` (project root)
3. If neither exists, ask user which to create

```bash
# Check which exists
ls -la .claude/CLAUDE.md CLAUDE.md 2>/dev/null
```

## Phase 1: Session Analysis

Review the conversation history for:

1. **Corrections you received** - Where user said "no", "wrong", "actually...", "instead..."
2. **Explicit instructions** - Direct guidance like "always do X", "never do Y", "use Z pattern"
3. **Repeated patterns** - Things explained multiple times
4. **Gotchas discovered** - Unexpected behaviors, edge cases, project quirks
5. **Workflow preferences** - How user wants things done

**If `$ARGUMENTS` provided**: Focus extraction on that topic area.

## Phase 2: Distill to Instructions

Transform raw learnings into **actionable instructions**:

| Bad (Verbose)                            | Good (Actionable)                |
| ---------------------------------------- | -------------------------------- |
| "The user mentioned that they prefer..." | "Always use X pattern"           |
| "We discovered that the API..."          | "API X requires Y header"        |
| "After some discussion..."               | "Run `make lint` before commits" |

### Instruction Format

```markdown
## [Section Name]

- **Do**: Concrete action
- **Don't**: Anti-pattern to avoid
- **When**: Trigger condition → action
- **Command**: `specific command to run`
```

## Phase 3: Categorize Learnings

Group into standard sections:

| Category             | Examples                             |
| -------------------- | ------------------------------------ |
| **Project Patterns** | Architecture, naming, file structure |
| **Code Style**       | Formatting, idioms, error handling   |
| **Workflows**        | Build, test, deploy procedures       |
| **Gotchas**          | Edge cases, known issues, quirks     |
| **Tools**            | CLI commands, scripts, integrations  |
| **Don'ts**           | Anti-patterns, things to avoid       |

## Phase 4: Present & Confirm

Show user the proposed additions:

```markdown
## Proposed Learnings

### [Category]

- Learning 1
- Learning 2

---

**Target**: `path/to/CLAUDE.md`
**Action**: Append to existing sections or create new
```

**STOP**: Use `AskUserQuestion`:

| Header | Question                       | Options                                                                                                                                  |
| ------ | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Action | How should I update CLAUDE.md? | 1. **Append all** - Add to file 2. **Review each** - Approve individually 3. **Edit first** - Let me modify 4. **Cancel** - Don't update |

## Phase 5: Apply Updates

Based on user choice:

### Append Strategy

1. **Read existing CLAUDE.md** to understand structure
2. **Match sections** - Add to existing sections if they exist
3. **Create new sections** - Only if category doesn't exist
4. **Date-stamp new learnings** (optional, at end):
   ```markdown
   <!-- Learned: 2025-01-05 -->
   ```

### Deduplication

Before adding, check if similar instruction exists:

- Skip exact duplicates
- Merge similar items
- Strengthen weak instructions with specific details

## Output Format

After update:

```
LEARNED
=======
Target: .claude/CLAUDE.md
Added: X new instructions
Sections: [list of sections updated]

Summary:
- [brief list of key learnings]
```

## Examples

**Session**: User corrected error handling pattern 3 times

```markdown
## Error Handling

- Wrap all errors with context: `fmt.Errorf("operation: %w", err)`
- Never use bare `return err`
- Use `errors.Is()` for sentinel checks
```

**Session**: User explained project-specific workflow

```markdown
## Workflows

### Before PR

1. `make fmt` - Format code
2. `make test` - Run tests
3. `make lint` - Check style
4. Never push directly to main
```

**Session**: User mentioned a gotcha

```markdown
## Gotchas

- `UserService.Get()` returns `nil, nil` when not found (not an error)
- Config files in `config/` are loaded alphabetically
- CI runs on Ubuntu, local is macOS - watch for path differences
```

---

**Execute extraction now. Analyze this session for learnings.**
