# Python principles and verification

Read this before generating Python code. Covers the stdlib-first stance,
typing/control-flow/error-handling principles, the no-destructive-commands safety
rule, and the post-generation verification loop.

## Safety

Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

## Core Philosophy

### Stdlib and Mature Libraries First

- Prefer Python stdlib solutions; prefer dataclasses over attrs, pathlib over os.path
- Add a library only when real requirements beat stdlib simplicity

### Type Hints Everywhere (No Any)

- Use `X | Y` union syntax (3.10+), PEP 695 generics (3.12+)
- Use Protocol for structural typing (duck typing)
- Avoid Any—use concrete types or generics

### Protocol Over ABC

- Protocol for implicit interface satisfaction
- ABC only when runtime isinstance() needed

### Flat Control Flow

- Guard clauses with early returns
- Pattern matching to flatten conditionals
- Maximum 2 levels of nesting

### Explicit Error Handling

- Custom exception hierarchy for domain errors
- Raise early, handle at boundaries
- Specific exception types (never bare `except Exception`)
- Multiple exception types use tuple syntax: `except (KeyError, json.JSONDecodeError) as exc:`. Avoid bare comma syntax (`except KeyError, json.JSONDecodeError:`): it is Python 3.14-only, cannot be used with `as exc`, and is visually easy to confuse with legacy exception binding.

### Structured Logging

- Use `structlog` for structured, contextualized logging
- Never use `print()` for operational output

## Verify Generated Code

After generating or modifying code, run the full check loop:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

Use the project's configured commands if different. If checks fail:

1. Fix lint/format issues (ruff autofix handles most)
2. Fix type errors flagged by pyright
3. Re-run: `ruff check . && ruff format --check . && pyright`
4. Repeat until all checks pass — only then consider the task complete
