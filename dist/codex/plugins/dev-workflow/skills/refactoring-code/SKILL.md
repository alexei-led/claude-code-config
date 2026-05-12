---
description: Batch refactoring via MorphLLM edit_file. Use for "refactor across files",
  "batch rename", "update pattern everywhere", large files (500+ lines), 5+ edits
  in same file, or applying an approved architecture-deepening refactor. NOT for single-file
  targeted edits (use built-in Edit) or code review (use reviewing-code).
name: refactoring-code
---

# Fast Refactoring with MorphLLM

MorphLLM `edit_file` provides semantic code merging at 10,500+ tokens/sec with 98% accuracy. Use the MorphLLM `edit_file` / batch refactoring workflow for broad changes. Refactoring here means behavior-preserving change or architecture deepening, not cosmetic churn.

Critical rule: preserve existing behavior unless the user explicitly asks for a behavior change. State the preservation target before editing.

## When to Use edit_file

Use `edit_file` when:

- Multi-file batch refactoring
- Style/pattern update everywhere
- Complex prompt → many changes
- Structural refactoring at scale
- 5+ files need same pattern

Use Built-in Edit/MultiEdit when:

- Single file, clear edit
- 2-3 targeted replacements
- Need clear diff to review/tune
- Simple rename (replace_all)
- Straightforward single-file work

## Key Features

- **Semantic merge**: Understands code structure, not just text
- **Speed**: 10,500 tok/s vs 180 tok/s streaming
- **Accuracy**: 98% success rate on edge cases
- **dryRun**: Preview changes before applying

## Architecture Deepening

When the request is architectural, use this vocabulary:

- **Module** — anything with an interface and implementation.
- **Interface** — everything callers must know: types, invariants, error modes, config, performance.
- **Seam** — where an interface lives.
- **Adapter** — concrete thing satisfying an interface at a seam.
- **Depth** — lots of behavior behind a small interface.
- **Leverage** — caller value from depth.
- **Locality** — change and verification concentrated in one place.

Deletion test: if deleting a module makes complexity vanish, it was a pass-through. If complexity reappears across callers, the module was earning its keep.

Seam rule: one adapter means a hypothetical seam; two adapters means a real seam. Do not add interfaces without real variation.

Read relevant `CONTEXT.md`, `CONTEXT-MAP.md`, and ADRs when present. Preserve domain names.

## Workflow

### Standard Refactoring

```
1. Use WarpGrep or semantic search to find all locations needing change
2. State: "Behavior must be preserved unless the user explicitly requested a behavior change."
3. Use MorphLLM `edit_file` or the batch refactoring workflow for each batch/file, grouping related edits
4. Batch all edits for the same file into one edit operation
5. Verify with lint/test
6. Delete obsolete shallow tests once deeper interface tests cover the behavior
```

For multi-file renames, say this is a batch refactor, map all occurrences before editing, use the batch refactoring tool/workflow by name, preserve behavior, and run relevant lint/tests after the rename.

### High-Stakes Changes (dryRun)

```
1. Call edit_file with dryRun: true
2. Review preview output
3. If approved, call again with dryRun: false
```

## Parameters

```
path: "/absolute/path/to/file"
code_edit: "changed lines with // ... existing code ... markers"
instruction: "brief description of changes"
dryRun: false (set true to preview)
```

## Edit Format

Use `// ... existing code ...` markers for unchanged sections:

```typescript
// ... existing code ...
function updatedFunction() {
  // new implementation
}
// ... existing code ...
```

## Common Patterns

### Batch Error Handling

```
instruction: "Add error wrapping to all repository methods"
code_edit: Shows only changed functions with context markers
```

### Import Updates

```
instruction: "Update imports from old-pkg to new-pkg"
code_edit: Shows import section with changes
```

### Multi-Location Rename

```
instruction: "Rename getUserById to findUser throughout file"
code_edit: Shows all locations with changes
```

## Failure handling

- `edit_file` unavailable → fall back to built-in Edit/MultiEdit; warn the user that large batches may be slower
- Tests fail after a batch edit → revert the last file edit, inspect the diff, and fix the conflict before continuing
- Scope unclear (user says "refactor this") → ask: "Which files and what behavior to preserve?" before touching anything

## Tips

- Batch all edits to same file in one call
- Include enough context to locate changes precisely
- Preserve exact indentation in code_edit
- Use WarpGrep first to understand scope
- Run tests after each file to catch issues early
- Keep old public behavior stable unless the user explicitly requested behavior change
- Prefer tests through the deepened module interface over tests of extracted helpers
