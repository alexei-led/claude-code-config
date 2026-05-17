# Python Architecture Reference

Language-specific over-abstraction and dead-code patterns for Python 3.12+. The shared modularity model lives in [LANGUAGE.md](LANGUAGE.md) and [DEEPENING.md](DEEPENING.md) — this file supplies only the Python-specific smells and detection.

## Run tooling first

```bash
# Check for style issues and unused imports
ruff check .

# Find dead code
vulture . --min-confidence 80
```

LSP navigation for unused and over-abstracted code:

- `findReferences` — check if exported symbols are actually used
- `goToImplementation` — find how many implementations a Protocol has
- `incomingCalls` — verify functions are called (dead code detection)
- `workspaceSymbol` — search for duplicate/similar function names

## Over-abstraction

### ABC with single subclass

Abstract base class with only one implementation. Apply the deletion test from [LANGUAGE.md](LANGUAGE.md): would deleting the ABC cause complexity to vanish (it was a pass-through), or would it reappear across N callers?

### Protocol with single implementation

Protocol defined but only one class ever satisfies it — a hypothetical seam with no real variation (see [DEEPENING.md](DEEPENING.md): one adapter = hypothetical seam). Remove until a second implementation exists.

### Unnecessary inheritance

Class inherits but overrides nothing. The inheritance adds interface surface with no depth.

### Factory for one type

Factory pattern when only one type is produced. A factory that always returns the same concrete type is a pass-through.

### Wrapper classes

Classes that just forward to another object with no transformation — the deletion test applies: would the wrapper's callers bear any additional complexity if it were deleted?

## Legacy code to remove (Python 3.14+)

These constructs are either defaults or superseded in modern Python — remove them:

- `from __future__ import annotations` — default in 3.14, remove
- String-quoted type hints: forward references work without quotes
- `TYPE_CHECKING` guard blocks: often unnecessary with deferred annotations
- `typing` module imports for builtins: `List`, `Dict`, `Optional`, `Tuple` → use `list`, `dict`, `X | None`, `tuple` directly

Stdlib simplifications available now:

- `pathlib.copy` / `pathlib.move` (3.14): replace `shutil` patterns
- Union syntax: `X | None` instead of `Optional[X]` or `Union[X, None]`

## Dead code

- Unused imports, including legacy typing imports (detected by `ruff`)
- Unreachable code: code after `return`/`raise` that never executes
- Commented-out blocks: delete — git has history
- Unused parameters: function parameters never referenced (`vulture` catches these)
- Legacy compatibility imports: `from __future__`, `TYPE_CHECKING` blocks no longer needed

## Unnecessary complexity

### Nested comprehensions

Triple-nested list comprehensions — extract to a named function. Two levels is the readability limit.

### Complex lambda

Lambda with multiple operations — use `def` instead.

### Nested ternaries

Replace with `match` — the Python-idiomatic simplification:

```python
# BAD: nested ternary
status = "admin" if is_admin else "user" if is_user else "guest" if is_guest else "unknown"

# GOOD: match statement
match role:
    case "admin": status = "admin"
    case "user":  status = "user"
    case "guest": status = "guest"
    case _:       status = "unknown"
```

## Failure handling

- If `ruff check` fails to run: note the failure and proceed with manual dead-code and complexity review.
- If `vulture` is not installed: skip dead-code automation and rely on LSP `findReferences` and `incomingCalls`.
- If LSP tools are unavailable: skip unused-symbol detection; flag this limitation in findings.
- If the codebase is intentionally minimal (e.g., a library stub): note this and limit scope to dead code only.
