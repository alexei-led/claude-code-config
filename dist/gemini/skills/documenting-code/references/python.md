# Python Documentation Slice

Language-specific documentation conventions for Python 3.12+. The host skill supplies workflow and verification — this file supplies only the Python doc-comment conventions and examples.

## run tooling first

```bash
# render module docs
pydoc src.module_name

# Sphinx build (if configured)
sphinx-build -b html docs/ docs/_build/
```

Use LSP to verify coverage:

- `documentSymbol` — list all exported symbols in a file
- `hover` — check existing documentation on symbols
- `findReferences` — verify documented APIs are used correctly

## docstring conventions

Use Google-style docstrings consistently. Type hints in signatures reduce the need to repeat type info in docstring bodies.

### module docstring

```python
"""User service module for user management operations.

This module provides the UserService class for creating, updating,
and managing user accounts.

Example:
    service = UserService(repository=repo)
    user = service.create_user(email="user@example.com")

Attributes:
    DEFAULT_TIMEOUT: Default timeout for operations (30 seconds)
"""

DEFAULT_TIMEOUT = 30
```

### class docstring

```python
class UserService:
    """Service for user management operations.

    Handles user creation, validation, and persistence through
    the provided repository.

    Args:
        repository: Data access layer for user persistence
        logger: Optional logger instance

    Example:
        service = UserService(repository=UserRepository())
        user = service.create_user(email="test@example.com")
    """

    def __init__(self, repository: UserRepository, logger: Logger | None = None):
        self.repository = repository
        self.logger = logger or get_default_logger()
```

### function docstring

```python
def create_user(self, email: str, name: str | None = None) -> User:
    """Create a new user with the provided information.

    Args:
        email: User's email address (must be unique)
        name: Optional display name

    Returns:
        The created User object with generated ID

    Raises:
        ValueError: If email is invalid or already exists
        RepositoryError: If database operation fails

    Example:
        user = service.create_user(
            email="john@example.com",
            name="John Doe"
        )
    """
```

### TypedDict docstring

```python
from typing import TypedDict

class UserDict(TypedDict):
    """Dictionary representation of a User.

    Attributes:
        id: Unique identifier
        email: User's email address
        name: Display name (optional)
    """
    id: str
    email: str
    name: str | None
```

## type hints as documentation

- All public functions need complete type hints including return type.
- Use `X | None` instead of `Optional[X]`.
- Use `list[str]` not bare `list`.
- Prefer deferred annotations (no string quotes needed in 3.12+).

## module-level documentation

- Include `__all__` to define the public API explicitly: `__all__ = ["User", "UserService", "Config"]`
- Include `__version__` in package `__init__.py`.
- Prefix private symbols with `_`; public functions without a docstring are a documentation gap.

## comment style

Lowercase, no trailing dots. Comments explain why, not what.

Delete if a competent developer would understand without it, or if it paraphrases the code.

## failure handling

- If `pydoc` fails (import errors, missing module), note the failure and proceed with manual docstring inspection.
- If Sphinx build fails, skip build-artifact checks and focus on source docstring review.
- If LSP is unavailable, read files directly; note the limitation.
- If the codebase has no public API (all private symbols), note this and skip public API checks.
