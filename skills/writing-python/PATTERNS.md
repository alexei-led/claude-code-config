# Python Patterns Reference

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

## Type Hints

### Functions

```python
def get_user(user_id: str) -> User | None:
    ...

def process_items(items: Iterable[Item], *, limit: int = 100) -> list[Result]:
    ...

async def fetch(url: str, timeout: float = 30.0) -> bytes:
    ...
```

### Generics

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### Protocol (Structural Typing)

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

def process(source: Readable) -> str:
    data = source.read()
    return data.decode()
```

### TypedDict

```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: str
    name: str
    email: NotRequired[str]
```

## Error Handling

### Custom Exceptions

```python
class AppError(Exception):
    pass

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

### Error Handling Pattern

```python
def get_user(user_id: str) -> User:
    user = db.get(user_id)
    if user is None:
        raise NotFoundError("User", user_id)
    return user
```

## Configuration

### Environment-Based

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

## Async Patterns

### Concurrent Tasks

```python
import asyncio

async def fetch_all(urls: list[str]) -> list[bytes]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Timeout

```python
async def fetch_with_timeout(url: str, timeout: float = 30.0) -> bytes:
    async with asyncio.timeout(timeout):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.read()
```

## Context Managers

### Resource Management

```python
from contextlib import contextmanager

@contextmanager
def open_db_connection(url: str):
    conn = create_connection(url)
    try:
        yield conn
    finally:
        conn.close()
```

### Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session():
    session = await create_session()
    try:
        yield session
    finally:
        await session.close()
```

## Data Validation

### With Pydantic (when needed)

```python
from pydantic import BaseModel, EmailStr, field_validator

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()
```

## File Operations

### Pathlib

```python
from pathlib import Path

def process_files(directory: Path) -> list[Path]:
    return list(directory.glob("**/*.json"))

def read_config(path: Path) -> dict:
    return json.loads(path.read_text())
```

## Logging

### Structured Logging

```python
import logging
import sys

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

logger = logging.getLogger(__name__)
logger.info("Processing started", extra={"count": len(items)})
```

## Style Guidelines

- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Use `UPPER_CASE` for constants
- Prefer `pathlib.Path` over `os.path`
- Use f-strings for formatting
- Use context managers for resources
- Avoid mutable default arguments
