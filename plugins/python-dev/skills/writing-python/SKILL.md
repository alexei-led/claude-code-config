---
name: writing-python
description: Idiomatic Python 3.12+ development. Use when writing Python code, CLI tools, scripts, or services. Emphasizes stdlib, type hints, uv/ruff/pyright toolchain, and minimal dependencies.
user-invocable: false
context: fork
agent: python-engineer
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
---

# Python Development (3.12+)

## Core Philosophy

1. **Stdlib and Mature Libraries First**
   - Always prefer Python stdlib solutions
   - External deps only when stdlib insufficient
   - Prefer dataclasses over attrs, pathlib over os.path

2. **Type Hints Everywhere (No Any)**
   - Use `X | Y` union syntax (3.10+), PEP 695 generics (3.12+)
   - Use Protocol for structural typing (duck typing)
   - Avoid Any—use concrete types or generics

3. **Protocol Over ABC**
   - Protocol for implicit interface satisfaction
   - ABC only when runtime isinstance() needed

4. **Flat Control Flow**
   - Guard clauses with early returns
   - Pattern matching to flatten conditionals
   - Maximum 2 levels of nesting

5. **Explicit Error Handling**
   - Custom exception hierarchy for domain errors
   - Raise early, handle at boundaries
   - Specific exception types (never bare `except Exception`)

6. **Structured Logging**
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

- [PATTERNS.md](PATTERNS.md) - Code patterns and style
- [CLI.md](CLI.md) - CLI application patterns (Click)
- [TESTING.md](TESTING.md) - Testing with pytest

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

After generating code, always verify it passes checks:

```bash
ruff check . && ruff format --check . && pyright
```
