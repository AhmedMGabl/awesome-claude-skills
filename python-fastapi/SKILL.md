---
name: python-fastapi
description: Python FastAPI patterns covering async endpoints, Pydantic models, dependency injection, middleware, OAuth2 authentication, WebSockets, and OpenAPI documentation.
---

# Python FastAPI

This skill should be used when building APIs with Python FastAPI. It covers async endpoints, Pydantic models, dependency injection, auth, WebSockets, and auto-generated docs.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance async APIs with FastAPI
- Validate request/response data with Pydantic
- Use dependency injection for auth and database
- Generate OpenAPI/Swagger documentation
- Handle WebSocket connections

## Setup

```bash
pip install fastapi uvicorn[standard] pydantic
```

## Basic Application

```python
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, EmailStr
from typing import Optional

app = FastAPI(title="My API", version="1.0.0")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True

@app.get("/api/users", response_model=list[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    users = await user_service.list(page, limit)
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int = Path(..., ge=1)):
    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate):
    user = await user_service.create(data)
    return user
```

## Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await verify_token(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/api/profile")
async def get_profile(user = Depends(get_current_user)):
    return user
```

## Authentication

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@app.post("/api/auth/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"sub": str(user.id)}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}
```

## Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_timing(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    return response
```

## Error Handling

```python
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail},
    )
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

## Additional Resources

- FastAPI: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/
- Pydantic: https://docs.pydantic.dev/
