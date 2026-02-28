# Python Patterns Reference

## Contents

- [Project Structure](#project-structure)
- [Protocol-Based Interfaces](#protocol-based-interfaces)
- [Flat Control Flow: No Nested Conditions](#flat-control-flow-no-nested-conditions)
- [Type Hints (No Any)](#type-hints-no-any)
- [Error Handling](#error-handling)
- [Async Patterns](#async-patterns)
- [Configuration](#configuration)
- [Context Managers](#context-managers)
- [File Operations](#file-operations)
- [Style Summary](#style-summary)

## Project Structure

```
src/
└── mypackage/
    ├── __init__.py
    ├── __main__.py      # CLI entry
    ├── domain/          # Business logic
    ├── services/        # Operations
    └── adapters/        # External integrations
tests/
pyproject.toml
```

## Protocol-Based Interfaces

Protocols enable duck typing with type hints. Define at consumer (like Go interfaces).

### Pattern

```python
from typing import Protocol

# Protocol at consumer—defines what it needs
class UserStore(Protocol):
    def get(self, id: str) -> User | None: ...
    def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, store: UserStore):
        self.store = store  # accepts any matching impl

# Any class with matching methods satisfies the Protocol
class PostgresStore:
    def get(self, id: str) -> User | None: ...
    def save(self, user: User) -> None: ...

# Works! No explicit inheritance needed
service = UserService(PostgresStore())
```

### Protocol vs ABC

| Use Case                    | Choice   |
| --------------------------- | -------- |
| Duck typing with hints      | Protocol |
| Runtime isinstance() checks | ABC      |
| Implicit satisfaction       | Protocol |
| Explicit method enforcement | ABC      |

```python
# Protocol: implicit satisfaction (preferred)
class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

# ABC: explicit inheritance required
from abc import ABC, abstractmethod

class Readable(ABC):
    @abstractmethod
    def read(self, n: int = -1) -> bytes: ...
```

## Flat Control Flow: No Nested Conditions

### Guard Clauses Pattern

```python
# GOOD: flat, readable
def process_order(order: Order | None) -> Result:
    if order is None:
        raise ValueError("order required")
    if not order.id:
        raise ValueError("order ID required")
    if not order.items:
        raise ValueError("order must have items")
    if order.total <= 0:
        raise ValueError("invalid total")

    # Happy path at lowest nesting level
    return save_order(order)

# BAD: deeply nested
def process_order(order: Order | None) -> Result:
    if order is not None:
        if order.id:
            if order.items:
                if order.total > 0:
                    return save_order(order)
    raise ValueError("invalid order")
```

### Pattern Matching to Flatten

```python
# GOOD: match instead of if-elif chain
def handle_event(event: Event) -> None:
    match event:
        case ClickEvent(x=x, y=y):
            handle_click(x, y)
        case KeyEvent(code=code):
            handle_key(code)
        case ScrollEvent(delta=delta):
            handle_scroll(delta)
        case _:
            raise ValueError(f"Unknown event: {event}")

# GOOD: match on dict patterns
match response:
    case {"status": "success", "data": data}:
        return process_data(data)
    case {"status": "error", "message": msg}:
        raise ApiError(msg)
    case {"status": status}:
        raise ValueError(f"Unknown status: {status}")
```

### Extract Complex Conditions

```python
# GOOD: extract to functions
def can_process_payment(user: User, amount: float) -> bool:
    if not user.is_active:
        return False
    if user.balance < amount:
        return False
    if amount > MAX_TRANSACTION:
        return False
    return True

def process_payment(user: User, amount: float) -> Result:
    if not can_process_payment(user, amount):
        raise PaymentError("Cannot process payment")
    return execute_payment(user, amount)
```

## Type Hints (No Any)

### Concrete Types

```python
# GOOD: concrete types everywhere
def get_user(user_id: str) -> User | None:
    ...

def process_items(items: list[Item], *, limit: int = 100) -> list[Result]:
    ...

async def fetch(url: str, timeout: float = 30.0) -> bytes:
    ...

# BAD: unnecessary Any
def process(data: Any) -> Any:  # Don't do this
    ...
```

### Generics When Needed

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

def retry(fn: Callable[[], T], attempts: int = 3) -> T:
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
    raise RuntimeError("Unreachable")
```

### TypedDict for Dict Schemas

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: str
    name: str
    email: NotRequired[str]

def process_user(data: UserDict) -> User:
    return User(id=data["id"], name=data["name"])
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

class ValidationError(AppError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")
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
        user = get_user(user_id)
        return UserResponse.from_domain(user)
    except NotFoundError:
        raise HTTPException(status_code=404)
```

### Python 3.14 Exception Syntax

```python
# No parens needed for multiple exceptions (PEP 758, Python 3.14+)
except ValueError, TypeError, KeyError:
    handle_error()

# With binding (parens required when using 'as')
except (ValueError, TypeError) as e:
    log_error(e)
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
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()
```

## Configuration

### Dataclass-Based

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    database_url: str
    port: int = 8080
    debug: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            database_url=os.environ["DATABASE_URL"],
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
- Concrete types (no Any)
- `snake_case` for functions/variables
- `PascalCase` for classes
- `pathlib.Path` over `os.path`
- f-strings for formatting
- Context managers for resources
