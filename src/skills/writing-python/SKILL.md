---
description:
  Idiomatic Python 3.12+ development. Use when writing Python code, CLI
  tools, scripts, or services. Emphasizes stdlib, type hints, uv/ruff/pyright toolchain,
  and minimal dependencies. NOT for Go, TypeScript, or shell-only tasks.
name: writing-python
---

# Python Development (3.12+)

## Critical Output Rules

- State Python 3.12+ typing choices explicitly and include a small example when planning code: concrete types, `X | Y`, generics/Protocol where useful, and `Any` is not the default.
- Prefer stdlib first for small tools: `argparse`, `pathlib`, `json`, `dataclasses`, `urllib`, `typing`.
- Prefer flat control flow with guard clauses and early returns; keep the happy path visually obvious. In implementation plans, explicitly say validation/parsing should fail fast with guard clauses before the happy path summary logic.
- Include behavior tests with `pytest` for the happy path and invalid input/error paths.
- Include verification commands when code changes: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pyright` when configured.
- Keep dependencies minimal; add one only when real requirements beat stdlib simplicity. Dependency guidance must still mention typed boundaries and pytest coverage for the script.
- Do not run destructive shell commands. For broad or risky changes, state the risk and ask before acting.

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

### Structured Logging

- Use `structlog` for structured, contextualized logging
- Never use `print()` for operational output

## Quick Patterns

### Protocol-Based Dependency Injection

```python
from typing import Protocol

class UserStore(Protocol):
    def get(self, id: str) -> User | None: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, store: UserStore):
        self.store = store  # accepts any matching impl
```

### PEP 695 Generics (3.12+)

```python
# NEW: type parameter syntax (no TypeVar boilerplate)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

type Vector = list[float]  # type alias statement
```

### Dataclasses with Performance

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class StatusUpdate:
    raw_text: str
    display_label: str
    is_interactive: bool = False
```

### Flat Control Flow (No Nesting)

```python
def process(user: User | None) -> Result:
    if user is None:
        raise ValueError("user required")
    if not user.email:
        raise ValueError("email required")
    if not is_valid_email(user.email):
        raise ValueError("invalid email")
    return do_work(user)  # happy path at end
```

### Structured Logging

```python
import structlog
logger = structlog.get_logger()

logger.info("processing_started", user_id=user.id, count=len(items))
logger.error("operation_failed", error=str(e), context=ctx)
```

### Error Handling

```python
class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} not found: {id}")

# Exception chaining
raise ProcessingError("failed") from original_error
```

## Python 3.12+ Features (Adopt Now)

- **PEP 695 type params**: `def first[T](lst: list[T]) -> T` (no TypeVar)
- **F-string improvements**: nested quotes, multiline expressions
- **Pattern matching**: structural pattern matching (3.10+)

## Python 3.14 Features (When Targeting 3.14)

- **Deferred annotations**: No `from __future__ import annotations` needed
- **Template strings (t"")**: `t"Hello {name}"` returns Template (safe interpolation)
- **except without parens**: `except ValueError, TypeError:` (PEP 758)
- **concurrent.interpreters**: True multi-core parallelism
- **compression.zstd**: Zstandard in stdlib

## References

- [PATTERNS.md](references/PATTERNS.md) - Code patterns and style
- [CLI.md](references/CLI.md) - CLI application patterns (Click)
- [TESTING.md](references/TESTING.md) - Testing with pytest

## Tooling

```bash
uv sync                              # Install deps from pyproject.toml
uv add pkg                           # Add dependency
uv run python script.py              # Run in project env
uv run --with pkg python script.py   # Run with one-off dep
uv run --extra dev pytest -v         # Run tests (dev group)
ruff check --fix .                   # Lint and autofix
ruff format .                        # Format
pyright src/                         # Type check (preferred)
deptry src                           # Dependency check
```

## Makefile Targets (Convention)

```makefile
make fmt          # ruff format
make lint         # ruff check
make typecheck    # pyright
make deptry       # dependency check
make test         # unit tests only
make check        # fmt + lint + typecheck + deptry + test
```

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

## Failure Cases

- **No pyproject.toml / ambiguous project root**: run `find . -name 'pyproject.toml'` to locate the project before generating code; do not assume a single root.
- **pyright or ruff failure after generation**: quote the failing line, state the cause, show the exact fix. Do not retry blindly—diagnose first. For pyright `Cannot access attribute` errors, check import paths and `__init__.py` exports before touching type annotations.
