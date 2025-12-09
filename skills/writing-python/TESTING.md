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

```python
from unittest.mock import Mock, patch, AsyncMock

def test_with_mock():
    mock_client = Mock()
    mock_client.fetch.return_value = {"status": "ok"}

    service = Service(client=mock_client)
    result = service.process()

    assert result == "ok"
    mock_client.fetch.assert_called_once()

@patch("mypackage.services.external_api")
def test_with_patch(mock_api):
    mock_api.call.return_value = {"data": "test"}

    result = process_data()

    assert result == "test"
```

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

- One assertion per test (when practical)
- Descriptive test names
- Use fixtures for setup
- Parametrize for multiple cases
- Keep tests independent
- Test behavior, not implementation
