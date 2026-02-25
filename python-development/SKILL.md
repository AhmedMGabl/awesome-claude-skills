---
name: python-development
description: Python development best practices including virtual environments, type hints, dataclasses, async/await, pytest testing, packaging, and modern Python patterns for building robust applications.
---

# Python Development

This skill should be used when the user needs to write, organize, or improve Python code. It covers environment setup, modern Python syntax, type annotations, testing with pytest, packaging, async programming, and production-ready patterns.

## When to Use This Skill

Use this skill when you need to:

- Set up Python virtual environments and project structure
- Write type-annotated Python code
- Build classes with dataclasses or Pydantic models
- Write async/await code with asyncio or aiohttp
- Test code with pytest and coverage
- Package and distribute Python projects
- Work with common libraries (requests, SQLAlchemy, FastAPI, etc.)
- Apply Python best practices and design patterns

## Project Setup

### Virtual Environments

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Or use uv (faster, modern alternative)
pip install uv
uv venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
uv pip install -r requirements.txt  # faster
```

### Project Structure

```
my-project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       ├── models.py
│       ├── utils.py
│       └── exceptions.py
├── tests/
│   ├── conftest.py
│   ├── test_core.py
│   └── test_models.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

### pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-package"
version = "0.1.0"
description = "My Python package"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing"
```

## Type Annotations

### Basic Types

```python
# Built-in types (Python 3.10+)
def process(items: list[str], count: int, flag: bool = False) -> dict[str, int]:
    return {item: i for i, item in enumerate(items[:count])}

# Optional and Union
def find_user(user_id: int) -> str | None:
    return db.get(user_id)

# Callable and TypeVar
from typing import Callable, TypeVar

T = TypeVar("T")

def apply(func: Callable[[T], T], value: T) -> T:
    return func(value)

# TypedDict for dicts with known structure
from typing import TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: str
    role: str  # required
    age: int | None  # optional with None default

# Protocol for structural typing (duck typing)
from typing import Protocol

class Serializable(Protocol):
    def to_dict(self) -> dict: ...
    def to_json(self) -> str: ...
```

### Dataclasses

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    roles: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    _password_hash: str = field(default="", repr=False)

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        self.email = self.email.lower()

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles

    def add_role(self, role: str) -> None:
        if role not in self.roles:
            self.roles.append(role)

# Frozen (immutable) dataclass
@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
```

### Pydantic Models (Runtime Validation)

```python
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int | None = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}  # allow ORM objects

# Usage
user_data = {"name": "Alice", "email": "alice@example.com", "password": "secure123"}
user = UserCreate(**user_data)
print(user.model_dump())  # {'name': 'Alice', 'email': ...}
print(user.model_dump_json())  # JSON string
```

## Async Programming

### asyncio Fundamentals

```python
import asyncio
import httpx
from typing import Any

# Basic async function
async def fetch_data(url: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

# Concurrent requests
async def fetch_all(urls: list[str]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        return [r.json() for r in responses if not isinstance(r, Exception)]

# asyncio.TaskGroup (Python 3.11+)
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data("https://api.example.com/users"))
        task2 = tg.create_task(fetch_data("https://api.example.com/posts"))

    users = task1.result()
    posts = task2.result()
    return users, posts

# Async context managers
class AsyncDatabase:
    async def __aenter__(self):
        self.conn = await create_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

async def use_db():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
    return result

# Async generators
async def paginate(url: str, page_size: int = 100):
    page = 1
    while True:
        data = await fetch_data(f"{url}?page={page}&size={page_size}")
        items = data.get("items", [])
        if not items:
            break
        for item in items:
            yield item
        page += 1

async def process_all():
    async for item in paginate("https://api.example.com/items"):
        process(item)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="My API", version="1.0.0")

# Dependency injection
async def get_db():
    db = await create_db_connection()
    try:
        yield db
    finally:
        await db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    user = await verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Route with full type safety
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await db.users.insert_one(user_data.model_dump())
    return UserResponse.model_validate(user)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db=Depends(get_db)) -> UserResponse:
    user = await db.users.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## Testing with pytest

### Test Structure

```python
# tests/conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db():
    """Mock database fixture."""
    db = AsyncMock()
    db.users.find_one.return_value = None
    db.users.insert_one.return_value = {"id": 1, "name": "Test"}
    return db

@pytest.fixture
def sample_user():
    return {"name": "Alice", "email": "alice@example.com", "password": "secure123"}

# tests/test_core.py
import pytest
from my_package.core import UserService
from my_package.models import UserCreate

class TestUserService:
    def test_create_user_valid(self, mock_db, sample_user):
        service = UserService(mock_db)
        result = service.validate_user(UserCreate(**sample_user))
        assert result.email == "alice@example.com"

    def test_create_user_invalid_email(self):
        with pytest.raises(ValueError, match="Invalid email"):
            UserCreate(name="Bob", email="not-an-email", password="secure123")

    @pytest.mark.parametrize("password,valid", [
        ("short", False),
        ("longenough", True),
        ("", False),
        ("12345678", True),
    ])
    def test_password_validation(self, password, valid):
        if valid:
            user = UserCreate(name="Test", email="t@t.com", password=password)
            assert user.password == password
        else:
            with pytest.raises(ValueError):
                UserCreate(name="Test", email="t@t.com", password=password)

    @pytest.mark.asyncio
    async def test_async_create_user(self, mock_db, sample_user):
        service = UserService(mock_db)
        user = await service.create(UserCreate(**sample_user))
        assert user.id == 1
        mock_db.users.insert_one.assert_called_once()
```

### Mocking

```python
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

# Patch external calls
@patch("my_package.services.httpx.AsyncClient")
async def test_fetch_user(mock_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Alice"}
    mock_response.raise_for_status = MagicMock()
    mock_client.return_value.__aenter__.return_value.get = AsyncMock(
        return_value=mock_response
    )

    from my_package.services import fetch_user
    user = await fetch_user(1)
    assert user["name"] == "Alice"

# Context manager mock
def test_with_context():
    with patch("builtins.open", create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = "file content"
        from my_package.utils import read_config
        content = read_config("config.txt")
        assert content == "file content"
```

## Error Handling

```python
# Custom exceptions
class AppError(Exception):
    """Base application exception."""
    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    pass

class ValidationError(AppError):
    pass

class DatabaseError(AppError):
    pass

# Result pattern (avoid exceptions for expected failures)
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

@dataclass
class Result(Generic[T]):
    value: T | None
    error: Exception | None

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        return cls(value=value, error=None)

    @classmethod
    def err(cls, error: Exception) -> "Result[T]":
        return cls(value=None, error=error)

    @property
    def is_ok(self) -> bool:
        return self.error is None

# Usage
def find_user(user_id: int) -> Result[User]:
    try:
        user = db.get(user_id)
        if not user:
            return Result.err(NotFoundError(f"User {user_id} not found"))
        return Result.ok(user)
    except Exception as e:
        return Result.err(DatabaseError(str(e)))

result = find_user(42)
if result.is_ok:
    print(result.value.name)
else:
    handle_error(result.error)
```

## Common Patterns

### Context Managers

```python
from contextlib import contextmanager, asynccontextmanager

@contextmanager
def timer(label: str):
    import time
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}s")

with timer("database query"):
    results = db.query("SELECT * FROM users")

@asynccontextmanager
async def managed_connection(url: str):
    conn = await create_connection(url)
    try:
        yield conn
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()
```

### Decorators

```python
import functools
import time
from typing import Callable, TypeVar

F = TypeVar("F", bound=Callable)

def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Retry decorator with exponential backoff."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = delay * (2 ** attempt)
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s")
                    time.sleep(wait)
        return wrapper  # type: ignore
    return decorator

def cache_result(ttl_seconds: int = 300):
    """Simple TTL cache decorator."""
    cache: dict = {}

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper  # type: ignore
    return decorator

@retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
@cache_result(ttl_seconds=60)
def fetch_config(key: str) -> str:
    return requests.get(f"/config/{key}").text
```

## Code Quality Tools

```bash
# Linting and formatting
ruff check src/             # fast linter
ruff format src/            # formatter (replaces black)
mypy src/                   # type checking

# Run tests with coverage
pytest --cov=src --cov-report=html

# Pre-commit hooks
pip install pre-commit
# .pre-commit-config.yaml:
# repos:
#   - repo: https://github.com/astral-sh/ruff-pre-commit
#     hooks: [ruff, ruff-format]
#   - repo: https://github.com/pre-commit/mirrors-mypy
#     hooks: [mypy]

pre-commit install
pre-commit run --all-files
```

## Additional Resources

- Python docs: https://docs.python.org/3/
- Pydantic: https://docs.pydantic.dev/
- FastAPI: https://fastapi.tiangolo.com/
- pytest: https://docs.pytest.org/
- Ruff linter: https://docs.astral.sh/ruff/
- asyncio: https://docs.python.org/3/library/asyncio.html
