---
description: Token-efficient code navigation via AST parsing. Use when exploring file
  structure, cross-file symbol discovery, or targeted function extraction with smart_outline,
  smart_search, and smart_unfold. 10-20x fewer tokens than reading full files. NOT
  for semantic cross-file flow tracing (use searching-code/WarpGrep) or full-file
  content where AST structure is irrelevant.
name: smart-explore
---

<!-- Pi platform guidance -->
<!-- Use Pi tool names exactly: read, bash, edit, write, ask_user_question, structured_output, todo, Agent, get_subagent_result, steer_subagent, web_search, web_answer, web_research. -->
<!-- Use Agent, get_subagent_result, and steer_subagent for delegated work. -->
<!-- Use ctx7 or npx ctx7@latest through bash when Context7 documentation lookup is required. -->

# Smart Explore in Pi

Use cheap local structure before reading large files. The goal is orientation,
not pageantry.

## Workflow

1. Use `fd` to find candidate files.
2. Use `rg` for symbols, imports, routes, handlers, config keys, and tests.
3. Use language-native tools when available:
   - Python: `python -m ast`, `ruff`, `pyright`
   - Go: `go list`, `go test`, `go doc`, `gofmt -w` only when editing
   - TypeScript: `tsc --noEmit`, `bun test`, `rg 'export |function |class '
4. Read only the relevant ranges or small files.
5. Return an outline with exact paths and line references.

## Commands

```bash
fd '\.(go|py|ts|tsx|js|jsx)$'
rg -n 'class |def |func |export |interface |type '
rg -n 'TODO|FIXME|panic\(|throw new|console\.log'
```

## Output Contract

```markdown
## Smart Explore

### Files

- `path` — why it matters

### Symbols

- `path:line` — symbol and role

### Edges

- caller -> callee or import relationship

### Read Next

1. `path:line-range` — reason
```
