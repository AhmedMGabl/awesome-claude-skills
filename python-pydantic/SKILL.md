---
name: python-pydantic
description: Python Pydantic patterns covering model definitions, field validators, custom types, nested models, settings management, JSON Schema generation, and serialization.
---

# Python Pydantic

This skill should be used when validating and serializing data in Python with Pydantic. It covers models, validators, custom types, settings, and JSON Schema.

## When to Use This Skill

Use this skill when you need to:

- Validate request data and configuration
- Define typed data models with defaults
- Use custom validators and field constraints
- Manage application settings from env vars
- Generate JSON Schema from models

## Setup

```bash
pip install pydantic pydantic-settings
```

## Basic Models

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)
    bio: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Usage
user = User(id=1, name="Alice", email="alice@example.com", age=30)
print(user.model_dump())       # dict
print(user.model_dump_json())  # JSON string
```

## Field Validators

```python
from pydantic import BaseModel, field_validator, model_validator

class CreateUser(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("must be alphanumeric")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("must contain uppercase letter")
        return v

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self
```

## Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str = "US"
    zip_code: str

class UserProfile(BaseModel):
    user: User
    address: Address
    interests: list[str] = []
    metadata: dict[str, str] = {}

# Parse from nested dict
data = {
    "user": {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
    "address": {"street": "123 Main St", "city": "NYC", "zip_code": "10001"},
    "interests": ["coding", "music"],
}
profile = UserProfile(**data)
```

## Custom Types

```python
from pydantic import BaseModel
from typing import Annotated
from pydantic import AfterValidator

def validate_slug(v: str) -> str:
    if not all(c.isalnum() or c == "-" for c in v):
        raise ValueError("slug must contain only alphanumeric and hyphens")
    return v.lower()

Slug = Annotated[str, AfterValidator(validate_slug)]

class Post(BaseModel):
    title: str
    slug: Slug
    body: str
```

## Settings Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str
    allowed_hosts: list[str] = ["localhost"]

    model_config = {
        "env_file": ".env",
        "env_prefix": "APP_",
    }

settings = Settings()
print(settings.database_url)  # from APP_DATABASE_URL env var
```

## Serialization Control

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    password: str = Field(exclude=True)  # never serialize

    model_config = {
        "from_attributes": True,  # parse from ORM objects
    }

# Selective serialization
user.model_dump(include={"id", "name"})
user.model_dump(exclude={"password"})
user.model_dump(exclude_none=True)
user.model_dump(by_alias=True)
```

## JSON Schema

```python
# Generate JSON Schema
schema = User.model_json_schema()
print(json.dumps(schema, indent=2))

# Validate from JSON
user = User.model_validate_json('{"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30}')
```

## Additional Resources

- Pydantic: https://docs.pydantic.dev/
- Pydantic Settings: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- Migration Guide: https://docs.pydantic.dev/latest/migration/
