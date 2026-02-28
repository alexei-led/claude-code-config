# Python Testing Reference

## Framework: pytest

```bash
uv add --dev pytest pytest-asyncio pytest-cov
pytest -v
pytest --cov=src
```

## Basic Tests

```python
def test_validate_email_valid():
    assert validate_email("user@example.com") is None

def test_validate_email_empty():
    with pytest.raises(ValidationError, match="email required"):
        validate_email("")

def test_validate_email_invalid():
    with pytest.raises(ValidationError, match="invalid format"):
        validate_email("invalid")
```

## Parametrized Tests

```python
@pytest.mark.parametrize("email,expected_error", [
    ("user@example.com", None),
    ("", "email required"),
    ("invalid", "invalid format"),
    ("user@", "invalid format"),
])
def test_validate_email(email: str, expected_error: str | None):
    if expected_error:
        with pytest.raises(ValidationError, match=expected_error):
            validate_email(email)
    else:
        assert validate_email(email) is None
```

## Fixtures

```python
@pytest.fixture
def user_service(mock_repo):
    return UserService(repo=mock_repo)

@pytest.fixture
def mock_repo():
    return Mock(spec=UserRepository)

def test_get_user(user_service, mock_repo):
    mock_repo.get.return_value = User(id="123", name="Test")

    result = user_service.get_user("123")

    assert result.name == "Test"
    mock_repo.get.assert_called_once_with("123")
```

## Mocking

**Use `unittest.mock` + `pytest-mock` (mocker fixture) for all mocking.**

```python
from unittest.mock import Mock, patch, AsyncMock, create_autospec
```

### Mock Types

| Type                   | Use When                                                     |
| ---------------------- | ------------------------------------------------------------ |
| `Mock()`               | Basic mock, no magic methods                                 |
| `MagicMock()`          | Needs magic methods (`__len__`, `__iter__`, context manager) |
| `AsyncMock()`          | Async functions (`async def`)                                |
| `create_autospec(cls)` | Type-safe mock that validates signatures                     |

### Argument Matching (CRITICAL)

**Choose matchers deliberately—don't over-match or under-match:**

| Approach                | Use When                                          |
| ----------------------- | ------------------------------------------------- |
| Exact value             | Business-critical values (IDs, table names, keys) |
| `call_args` inspection  | Checking specific args without full match         |
| Custom `__eq__` matcher | Partial object matching                           |

```python
from unittest.mock import Mock, call

def test_with_exact_values():
    mock_repo = Mock()
    service = Service(repo=mock_repo)

    service.process_order("order-123", "customer-456")

    # GOOD: Exact values for business-critical parameters
    mock_repo.save.assert_called_once_with("order-123", "customer-456")

def test_with_partial_matching():
    mock_repo = Mock()
    service = Service(repo=mock_repo)

    service.create_user(email="test@example.com")

    # GOOD: Check specific arg without matching everything
    call_args = mock_repo.save.call_args
    assert call_args.kwargs["email"] == "test@example.com"
    assert call_args.kwargs["id"] is not None  # generated, just check exists

# Custom matcher for partial object matching
class HasAttrs:
    def __init__(self, **attrs):
        self.attrs = attrs
    def __eq__(self, other):
        return all(getattr(other, k, None) == v for k, v in self.attrs.items())
    def __repr__(self):
        return f"HasAttrs({self.attrs})"

def test_with_custom_matcher():
    mock_repo = Mock()
    service = Service(repo=mock_repo)

    service.create_user(email="test@example.com", name="Test")

    # GOOD: Match important fields, ignore generated ones
    mock_repo.save.assert_called_once_with(HasAttrs(email="test@example.com"))
```

### Type-Safe Mocking with autospec

**Use `create_autospec` or `spec=` to catch signature mismatches:**

```python
from unittest.mock import create_autospec

def test_with_autospec():
    # Validates call signatures at runtime
    mock_repo = create_autospec(UserRepository)

    mock_repo.get("123")  # OK
    mock_repo.get()  # TypeError: missing required argument

    # With pytest-mock
    mock_repo = mocker.Mock(spec=UserRepository)
```

### Patching Best Practices

**Patch where the object is looked up, not where it's defined:**

```python
# myapp/services.py
from myapp.clients import api_client

def process():
    return api_client.fetch()

# tests/test_services.py
@patch("myapp.services.api_client")  # Patch where it's USED
def test_process(mock_client):
    mock_client.fetch.return_value = {"data": "test"}
    result = process()
    assert result == {"data": "test"}

# With pytest-mock (preferred)
def test_process(mocker):
    mock_client = mocker.patch("myapp.services.api_client")
    mock_client.fetch.return_value = {"data": "test"}
    result = process()
    assert result == {"data": "test"}
```

### Async Mocking

```python
from unittest.mock import AsyncMock
import pytest

@pytest.mark.asyncio
async def test_async_service(mocker):
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"status": "ok"}

    service = Service(client=mock_client)
    result = await service.process()

    assert result == "ok"
    mock_client.fetch.assert_awaited_once()
```

### Common Mistakes to Avoid

- **Patching wrong target**: Patch where object is used, not defined
- **Missing spec/autospec**: Use `spec=` or `create_autospec` for important boundaries
- **Mock without assertions**: Always verify mocks were called correctly
- **Over-mocking**: Mock boundaries, not internals
- **Using Mock for async**: Use `AsyncMock` for async functions
- **Not resetting mocks**: Use fresh mocks per test (mocker fixture handles this)

## Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com")
    assert result is not None

@pytest.fixture
async def async_client():
    client = AsyncClient()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    result = await async_client.get("/users")
    assert result.status == 200
```

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_domain/
│   └── test_user.py
├── test_services/
│   └── test_user_service.py
└── test_integration/
    └── test_api.py
```

## conftest.py

```python
import pytest

@pytest.fixture
def sample_user():
    return User(id="123", name="Test", email="test@example.com")

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()
    session.close()
```

## Integration Tests

```python
@pytest.mark.integration
def test_database_integration(db_session):
    repo = UserRepository(db_session)

    user = User(name="Test", email="test@example.com")
    repo.save(user)

    result = repo.get(user.id)
    assert result.name == "Test"
```

Run integration tests:

```bash
pytest -m integration
pytest -m "not integration"  # Skip them
```

## Coverage

```bash
pytest --cov=src --cov-report=html
pytest --cov=src --cov-fail-under=80
```

## Guidelines

**CRITICAL: Zero tolerance for test waste**

- **No pointless tests**: Don't test trivial behavior (getters, constructors)
- **No naive tests**: Don't just test obvious happy paths—include edge cases
- **No duplicate tests**: Same scenario tested multiple ways → keep one, delete others
- **Combine with parametrize**: 2+ tests for same function → single `@pytest.mark.parametrize` (mandatory)
- **No comments in tests**: Tests should be self-explanatory unless logic is genuinely non-obvious

**Standard Guidelines**

- One assertion per test (when practical)
- Descriptive test names: `test_validate_email_empty_raises_error`
- Use fixtures for setup
- Use `pytest.param(..., id="desc")` for readable parametrized test names
- Keep tests independent
- Test behavior, not implementation
