---
name: python-pytest
description: Python pytest patterns covering fixtures, parametrize, mocking, async tests, markers, conftest, plugins, coverage, and test organization best practices.
---

# Python pytest

This skill should be used when writing tests with Python pytest. It covers fixtures, parametrize, mocking, async tests, markers, conftest, and coverage.

## When to Use This Skill

Use this skill when you need to:

- Write unit and integration tests with pytest
- Use fixtures for setup and teardown
- Parametrize tests with multiple inputs
- Mock dependencies with unittest.mock
- Test async code and measure coverage

## Setup

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

## Basic Tests

```python
def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_string_contains():
    result = greet("Alice")
    assert "Alice" in result
    assert result.startswith("Hello")
```

## Fixtures

```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Alice", email="alice@example.com")

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

@pytest.fixture(autouse=True)
def reset_cache():
    cache.clear()
    yield
    cache.clear()

def test_user_creation(sample_user):
    assert sample_user.name == "Alice"

def test_save_user(db_session, sample_user):
    db_session.add(sample_user)
    db_session.commit()
    assert sample_user.id is not None
```

## Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("Hello World", "HELLO WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500])
def test_error_handler(status_code):
    response = handle_error(status_code)
    assert response["error"] is True
```

## Mocking

```python
from unittest.mock import patch, MagicMock, AsyncMock

def test_fetch_user(mocker):
    mock_repo = mocker.patch("app.services.user_repo")
    mock_repo.get_by_id.return_value = User(id=1, name="Alice")

    result = user_service.get_user(1)
    assert result.name == "Alice"
    mock_repo.get_by_id.assert_called_once_with(1)

def test_send_email(mocker):
    mock_send = mocker.patch("app.email.send_email")
    register_user("alice@example.com")
    mock_send.assert_called_once_with("alice@example.com", subject="Welcome")

@patch("app.services.external_api")
def test_with_patch(mock_api):
    mock_api.fetch.return_value = {"status": "ok"}
    result = process_data()
    assert result["status"] == "ok"
```

## Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com")
    assert result is not None

@pytest.mark.asyncio
async def test_async_db(async_session):
    user = User(name="Alice", email="alice@example.com")
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    assert user.id is not None
```

## Markers

```python
@pytest.mark.slow
def test_large_dataset():
    process_large_file("data.csv")

@pytest.mark.integration
def test_database_connection():
    assert db.is_connected()

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_permissions():
    pass
```

## conftest.py

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    return app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: integration tests")
```

## Running Tests

```bash
pytest                           # run all tests
pytest tests/test_users.py       # specific file
pytest -k "test_create"          # match pattern
pytest -m "not slow"             # exclude markers
pytest --cov=app --cov-report=html  # coverage
pytest -x                        # stop on first failure
pytest -v                        # verbose output
pytest --tb=short                # shorter tracebacks
```

## Additional Resources

- pytest: https://docs.pytest.org/
- Fixtures: https://docs.pytest.org/en/stable/fixture.html
- Plugins: https://docs.pytest.org/en/stable/reference/plugin_list.html
