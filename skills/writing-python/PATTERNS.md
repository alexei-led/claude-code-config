# Python Patterns Reference

## Contents

- [Project Structure](#project-structure)
- [Module Conventions](#module-conventions)
- [Protocol-Based Interfaces](#protocol-based-interfaces)
- [Dataclasses](#dataclasses)
- [Flat Control Flow](#flat-control-flow)
- [Type Hints (No Any)](#type-hints-no-any)
- [Error Handling](#error-handling)
- [Structured Logging](#structured-logging)
- [Async Patterns](#async-patterns)
- [Configuration](#configuration)
- [Context Managers](#context-managers)
- [File Operations](#file-operations)
- [Style Summary](#style-summary)

## Project Structure

```
my-project/
├── pyproject.toml           # single source of truth
├── uv.lock                  # committed
├── .python-version          # e.g., "3.12"
├── Makefile                 # fmt, lint, typecheck, test, check
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── __main__.py      # CLI entry
│       ├── cli.py           # Click command groups
│       ├── config.py        # Config singleton (env + .env)
│       ├── domain/          # Business logic, models
│       ├── services/        # Operations, orchestration
│       ├── providers/       # External integrations (Protocol-based)
│       ├── handlers/        # Event/message handlers
│       └── utils.py         # Shared helpers
├── tests/
│   ├── conftest.py          # Root: env setup, shared fixtures
│   ├── my_package/
│   │   ├── conftest.py      # Unit fixtures, factories
│   │   └── test_*.py        # Unit tests
│   ├── integration/
│   │   ├── conftest.py      # Integration fixtures
│   │   └── test_*.py        # Real filesystem/processes
│   └── e2e/
│       └── test_*.py        # Full system tests (slow)
└── scripts/                 # Build/release helpers
```

## Module Conventions

Every `.py` file starts with a module-level docstring: one-sentence summary, then core responsibilities.

```python
"""Text message handling — step functions for the text_handler orchestrator.

Routes incoming text messages through a bool early-return chain:
UI guards → unbound topic → dead window recovery → message forwarding.
"""
```

**Naming:**
- Full variable names: `window_id` not `wid`, `session_id` not `sid`
- `snake_case` for functions/variables, `PascalCase` for classes
- Constants as module-level `UPPER_SNAKE_CASE`
- User-data keys: define string constants in a dedicated module

## Protocol-Based Interfaces

Define at consumer side (like Go interfaces). Any class with matching methods satisfies the Protocol.

```python
from typing import Protocol

class UserStore(Protocol):
    def get(self, id: str) -> User | None: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, store: UserStore):
        self.store = store

# Satisfies UserStore without inheritance
class PostgresStore:
    def get(self, id: str) -> User | None: ...
    def save(self, user: User) -> None: ...
```

### Protocol vs ABC

| Use Case                    | Choice   |
| --------------------------- | -------- |
| Duck typing with hints      | Protocol |
| Runtime isinstance() checks | ABC      |
| Implicit satisfaction       | Protocol |
| Explicit method enforcement | ABC      |

## Dataclasses

### Frozen + Slots for Performance

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class StatusUpdate:
    raw_text: str
    display_label: str
    is_interactive: bool = False
```

### Config Singleton

```python
@dataclass
class Config:
    api_url: str
    port: int = 8080
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_url=os.environ["API_URL"],
            port=int(os.environ.get("PORT", 8080)),
            debug=os.environ.get("DEBUG", "").lower() == "true",
        )
```

**Precedence:** CLI flag > env var > .env file > default value.

## Flat Control Flow

### Guard Clauses

```python
def process_order(order: Order | None) -> Result:
    if order is None:
        raise ValueError("order required")
    if not order.id:
        raise ValueError("order ID required")
    if not order.items:
        raise ValueError("order must have items")
    if order.total <= 0:
        raise ValueError("invalid total")
    return save_order(order)  # happy path at end
```

### Pattern Matching

```python
def handle_event(event: Event) -> None:
    match event:
        case ClickEvent(x=x, y=y):
            handle_click(x, y)
        case KeyEvent(code=code):
            handle_key(code)
        case _:
            raise ValueError(f"Unknown event: {event}")

# Dict pattern matching
match response:
    case {"status": "success", "data": data}:
        return process_data(data)
    case {"status": "error", "message": msg}:
        raise ApiError(msg)
```

### Extract Complex Conditions

```python
def can_process_payment(user: User, amount: float) -> bool:
    if not user.is_active:
        return False
    if user.balance < amount:
        return False
    if amount > MAX_TRANSACTION:
        return False
    return True
```

## Type Hints (No Any)

### PEP 695 Generics (3.12+)

```python
# NEW: type parameter syntax (preferred)
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None

type Vector = list[float]

# LEGACY: TypeVar (pre-3.12 codebases)
from typing import TypeVar
T = TypeVar("T")
def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### Concrete Types

```python
def get_user(user_id: str) -> User | None: ...
def process_items(items: list[Item], *, limit: int = 100) -> list[Result]: ...
async def fetch(url: str, timeout: float = 30.0) -> bytes: ...
```

### TypedDict for Dict Schemas

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: str
    name: str
    email: NotRequired[str]
```

### Literal for Constrained Strings

```python
from typing import Literal

PromptMode = Literal["replace", "wrap"]
OutputFormat = Literal["json", "csv", "table"]
```

## Error Handling

### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base for all application errors."""

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} not found: {id}")
```

### Raise Early, Handle at Boundaries

```python
# Service layer: raise specific errors
def get_user(user_id: str) -> User:
    user = db.get(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user

# API boundary: handle and convert
@app.get("/users/{user_id}")
def get_user_endpoint(user_id: str) -> UserResponse:
    try:
        return UserResponse.from_domain(get_user(user_id))
    except NotFoundError:
        raise HTTPException(status_code=404)
```

### Exception Chaining

```python
try:
    result = parse_config(path)
except json.JSONDecodeError as e:
    raise ConfigError(f"Invalid config: {path}") from e
```

### Specific Exception Types (Never Bare except)

```python
# GOOD
except OSError:
    handle_io_error()
except (ValueError, KeyError) as e:
    log_error(e)

# BAD
except Exception:  # too broad
    pass
```

## Structured Logging

Use `structlog` for structured, contextualized logging. Never `print()`.

```python
import structlog
logger = structlog.get_logger()

logger.info("processing_started", user_id=user.id, count=len(items))
logger.debug("config_loaded", dir=str(config.config_dir))
logger.warning("deprecated_usage", old=old_name, new=new_name)
logger.error("operation_failed", error=str(e), session_id=sid)
```

### Throttled Logging

For high-frequency events, throttle to avoid log spam:

```python
def log_throttled(key: str, msg: str, cooldown: float = 300.0) -> None:
    now = time.monotonic()
    if now - _last_logged.get(key, 0) >= cooldown:
        logger.info(msg)
        _last_logged[key] = now
```

## Async Patterns

### TaskGroup (3.11+)

```python
async def fetch_all(urls: list[str]) -> list[bytes]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_one(url)) for url in urls]
    return [task.result() for task in tasks]
```

### Timeout

```python
async def fetch_with_timeout(url: str, timeout: float = 30.0) -> bytes:
    async with asyncio.timeout(timeout):
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            return resp.content
```

### Task Exception Tracking

```python
def task_done_callback(task: asyncio.Task) -> None:
    if not task.cancelled() and task.exception():
        logger.error("background_task_failed", error=str(task.exception()))
```

## Configuration

### Dataclass with Env Precedence

```python
@dataclass
class Config:
    api_url: str
    port: int = 8080
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()  # python-dotenv
        return cls(
            api_url=os.environ["API_URL"],
            port=int(os.environ.get("PORT", 8080)),
            debug=os.environ.get("DEBUG", "").lower() == "true",
        )
```

## Context Managers

```python
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def db_transaction(conn: Connection):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

@asynccontextmanager
async def get_session():
    session = await create_session()
    try:
        yield session
    finally:
        await session.close()
```

## File Operations

```python
from pathlib import Path

def process_files(directory: Path) -> list[Path]:
    return list(directory.glob("**/*.json"))

def read_config(path: Path) -> dict:
    return json.loads(path.read_text())
```

## Style Summary

- Guard clauses reduce nesting (max 2 levels)
- Pattern matching for complex conditionals
- Protocol for interfaces (not ABC)
- Concrete types (no Any), PEP 695 generics (3.12+)
- `snake_case` for functions/variables, `PascalCase` for classes
- Full variable names (`window_id`, not `wid`)
- `pathlib.Path` over `os.path`
- `structlog` for logging, not `print()`
- f-strings for formatting
- Context managers for resources
- Dataclasses with `frozen=True, slots=True` for value objects
