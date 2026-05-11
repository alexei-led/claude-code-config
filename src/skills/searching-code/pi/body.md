# Codebase Search in Pi

Map code with verified file references. Do not read the whole repo because the
user sounds curious. Curiosity is not a query plan.

## Workflow

1. Clarify scope if the request is vague.
2. Check for domain docs first when present:
   - `CONTEXT.md`
   - `CONTEXT-MAP.md`
   - nearest `*/CONTEXT.md`
   - `docs/adr/*.md`
3. Use `fd` to find likely files and `rg` to find symbols, routes, handlers,
   tests, config keys, and shared types.
4. Read only the files or line ranges needed to verify the map.
5. For large searches, launch one bounded `Agent` with `scout` to gather
   compressed context. Keep the main loop in control.
6. Separate verified facts from guesses and unknowns.

## Useful Commands

```bash
fd 'auth|login|session|user'
rg -n 'login|authenticate|AuthService|Session|UserRepository'
rg -n 'func .*Handler|class .*Controller|router\.|app\.'
```

## Zoom-Out Mode

Use when the user says "zoom out", "map this area", "go up a layer", or sounds
lost in local details.

Return:

1. Flow with `file:line` references.
2. Key modules and responsibilities.
3. Callers, callees, shared types, and messages.
4. Unknowns or unverified assumptions.
5. Read-next list, top 3 files only.

## Output Contract

```markdown
## Code Map

### Scope

<what was mapped>

### Flow

1. `path:line` — fact
2. `path:line` — fact

### Modules

| Module | Files | Responsibility |
| ------ | ----- | -------------- |

### Unknowns

- <gap and how to verify>

### Read Next

1. `path` — why
```
